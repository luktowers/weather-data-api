from decimal import Decimal
import boto3
import json
from datetime import UTC, datetime
from typing import Optional, Dict, Any
from app.config import settings


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class StorageService:
    def __init__(self):
        self._dynamodb = boto3.resource(
            "dynamodb",
            endpoint_url=settings.DYNAMODB_ENDPOINT_URL,
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self._table = None

    @property
    def table(self):
        if self._table is None:
            self._table = self._dynamodb.Table("weather_forecasts")
        return self._table

    async def store_forecast(
        self, lat: float, lon: float, units: str, forecast_data: Dict[str, Any]
    ) -> bool:
        try:
            now = datetime.now(UTC)
            item = {
                "location_key": f"{lat}_{lon}_{units}",
                "forecast_data": json.dumps(forecast_data, cls=DecimalEncoder),
                "timestamp": now.isoformat(),
                "ttl": int(now.timestamp() + 3600),  # 1 hour TTL
            }
            self.table.put_item(Item=item)
            return True
        except Exception as e:
            print(f"Error storing forecast: {e}")
            return False

    async def get_forecast(
        self, lat: float, lon: float, units: str
    ) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(Key={"location_key": f"{lat}_{lon}_{units}"})

            if "Item" in response:
                item = response["Item"]
                current_time = int(datetime.now(UTC).timestamp())
                # Check if data is still valid (not expired)
                if current_time < item.get("ttl", 0):
                    return json.loads(item["forecast_data"])
            return None
        except Exception as e:
            print(f"Error retrieving forecast: {e}")
            return None
