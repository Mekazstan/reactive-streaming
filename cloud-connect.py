import confluent_cloud
import boto3
import time
from config import config

# Step 1: Connect to Confluent Cloud
confluent_cloud.configure(config["kafka"])

# Step 2: Create an environment on Confluent Cloud
environment_name = 'watcher'
environment = confluent_cloud.create_environment(environment_name, 'aws', 'us-east-1', 'free')

# Step 3: Create a cluster in the environment
cluster_name = 'watcher'
cluster = confluent_cloud.create_cluster(cluster_name, 'aws', 'us-east-1', 'free', environment['id'])

# Step 4: Setup Schema Registry
schema_registry = confluent_cloud.create_schema_registry(cluster['id'])

# Step 5: Create a ksqlDB cluster
ksql_cluster_name = 'watcher_ksql'
ksql_cluster = confluent_cloud.create_ksql_cluster(ksql_cluster_name, 'aws', 'us-east-1', 'free', cluster['id'], 1)


# Find the ksqlDB cluster by name
ksql_cluster = next(
    (cluster for cluster in confluent_cloud.list_ksql_clusters() if cluster['name'] == ksql_cluster_name),
    None
)

if ksql_cluster is None:
    print(f"Error: ksqlDB cluster '{ksql_cluster_name}' not found.")
    exit(1)


# Wait for ksqlDB cluster to be ready
while not confluent_cloud.is_ksql_cluster_ready(ksql_cluster['id']):
    time.sleep(15)

# Step 6: Execute SQL query to create a stream
data_producer_table = """
  CREATE STREAM youtube_videos (
    video_id VARCHAR KEY,
    title VARCHAR, 
    views INTEGER,
    comments INTEGER,
    likes INTEGER
  ) WITH (
    KAFKA_TOPIC='youtube_videos',
    PARTITIONS=1,
    VALUE_FORMAT='avro'
  );
"""


########### 2  ###########



# Execute the first SQL query to create a table
change_tracking_table_and_topic = """
  CREATE TABLE youtube_changes WITH (
    KAFKA_TOPIC = 'youtube_changes'
  ) AS
  SELECT
    video_id,
    latest_by_offset(title) AS title,
    latest_by_offset(comments, 2)[1] AS comments_previous,
    latest_by_offset(comments, 2)[2] AS comments_current,
    latest_by_offset(views, 2)[1] AS views_previous,
    latest_by_offset(views, 2)[2] AS views_current,
    latest_by_offset(likes, 2)[1] AS likes_previous,
    latest_by_offset(likes, 2)[2] AS likes_current
  FROM YOUTUBE_VIDEOS
  GROUP BY video_id;
"""

# Execute the second SQL query to select changes where likes_previous <> likes_current
select_changes_query = "SELECT * FROM YOUTUBE_CHANGES WHERE likes_previous <> likes_current EMIT CHANGES;"

ksql_query_telegram = """
  CREATE STREAM telegram_outbox (
    `chat_id` VARCHAR,
    `text` VARCHAR
  ) WITH (
    KAFKA_TOPIC='telegram_outbox',
    PARTITIONS=1,
    VALUE_FORMAT='avro'
  );
"""

youtube_changes_stream = """CREATE STREAM youtube_changes_stream WITH ( KAFKA_TOPIC = 'youtube_changes', VALUE_FORMAT = 'avro');"""

enable_message_sending_to_bot = """
    INSERT INTO telegram_outbox
    SELECT
    '920695486' AS `chat_id`,
    CONCAT(
        'Likes changed: ',
        CAST(likes_previous AS STRING),
        ' ==> ',
        CAST(likes_current AS STRING),
        '. ',
        title
    ) AS `text`
    FROM YOUTUBE_CHANGES_STREAM
    WHERE likes_current <> likes_previous;
"""

# Execute the queries
confluent_cloud.ksql_execute_statement(ksql_cluster['id'], data_producer_table)
confluent_cloud.ksql_execute_statement(ksql_cluster['id'], change_tracking_table_and_topic)
confluent_cloud.ksql_execute_statement(ksql_cluster['id'], select_changes_query)
confluent_cloud.ksql_execute_statement(ksql_cluster['id'], ksql_query_telegram)
confluent_cloud.ksql_execute_statement(ksql_cluster['id'], youtube_changes_stream)
confluent_cloud.ksql_execute_statement(ksql_cluster['id'], enable_message_sending_to_bot)