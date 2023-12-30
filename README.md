# Reactive Data Streaming Application
### Overview

This Reactive Data Streaming Application is designed to provide real-time alerts for changes in external systems that lack a dedicated alert API. This project specifically focuses on tracking changes to a YouTube video, allowing users to receive alerts when significant events occur, such as new comments on a video.

### Use Case: Tracking Changes to a YouTube Video

Scenario

Consider a scenario where you want to keep tabs on a YouTube channel that you don't own. You are interested in receiving immediate alerts whenever someone comments on a specific video from that channel.

### Strategy

It's strategy involves looking up a YouTube playlist, extracting information about the videos in that playlist using the YouTube Data API, and streaming the relevant statistics to Kafka. The data processing pipeline includes a Python script that periodically takes snapshots of the YouTube Data API, processes the changes, and sends alerts via a Kafka connector to a Telegram bot.

### Project Components

    Web Scraper (Python Script):
        Utilizes the YouTube Data API to retrieve information about videos in a specified playlist.
        Periodically takes snapshots of the API to capture changes over time.

    Kafka Streaming:
        Captures snapshots of YouTube video statistics and streams them to Kafka topics.

    Stream Processing:
        Monitors changes in the streamed data, identifying relevant events (e.g., new comments).

    Kafka Connector:
        Connects to Kafka topics, filters events of interest, and sends alerts to external systems.

    Telegram Bot:
        Receives and delivers alerts to users based on changes detected in the YouTube video statistics.

### Deployment (Yet to Implement)

The application is deployed using Docker containers, providing portability and ease of deployment. Docker files are provided to build the necessary images, and the application runs at 10-minute intervals to ensure timely updates.
Getting Started

    Requirements:
        Docker installed on your system.
        Access to the YouTube Data API (API key required).
        Kafka setup with topics for streaming data.

    Configuration:
        Set up the necessary configuration files, including API keys, Kafka connection details, and Telegram bot credentials.

    Building Docker Images:
        Use provided Dockerfiles to build images for the web scraper, Kafka streaming, and Kafka connector.

    Deploying Containers:
        Deploy the Docker containers using docker-compose or a similar orchestration tool.

### Usage

    Run the Application:
        Execute the Docker containers to start the web scraper, Kafka streaming, and Kafka connector.

    Monitor Alerts:
        Check the configured Telegram bot for alerts based on changes detected in the YouTube video statistics.