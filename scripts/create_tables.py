import boto3
from app.config import settings


def create_subscriptions_table():
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=settings.DYNAMODB_ENDPOINT_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    table = dynamodb.create_table(
        TableName="weather_subscriptions",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    # Wait until the table exists
    table.meta.client.get_waiter("table_exists").wait(TableName="weather_subscriptions")
    print("Table created successfully!")


if __name__ == "__main__":
    create_subscriptions_table()