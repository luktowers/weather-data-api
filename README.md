# Weather Data Collection and Notification API

A FastAPI-based weather data collection and notification system that integrates with OpenWeatherMap API and AWS services.

## Features

- Real-time weather data fetching
- Weather alerts and notifications via AWS SNS
- Subscription management with DynamoDB
- Weather picture uploads with S3
- Caching system for weather data
- Comprehensive test suite

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- AWS CLI (for local development with LocalStack)
- Poetry (for dependency management)

## Project Structure

## Environment Setup

1. Create a `.env` file in the root directory:

```sh
OPENWEATHER_API_KEY=your_api_key_here
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
DYNAMODB_ENDPOINT_URL=<http://localhost:4566>
SNS_ENDPOINT_URL=<http://localhost:4566>
```

- create virtual environment

```shell
pyenv virtualenv .venv
```

- activate virtual environment

```shell
pyenv activate .venv
```

- install dependencies

```shell
pip install -e .
```

2.run localstack

```shell
make deploy-local
```

3.Access the API documentation:

- Swagger UI: <http://localhost:8000/docs>
