import json
import logging
from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings

logger = logging.getLogger("carecircle.s3")


class S3Service:
    """S3 Persistence Layer with graceful in-memory fallback for offline/demo reliability."""

    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.use_s3 = False
        self.client = None
        self._memory_store: Dict[str, Any] = {}

        # Attempt to initialize boto3 S3 client if credentials exist
        try:
            kwargs = {"region_name": settings.AWS_REGION}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

            self.client = boto3.client("s3", **kwargs)
            # Test connectivity lightly or mark enabled
            self.use_s3 = True
            logger.info(f"Initialized boto3 S3 client for bucket: {self.bucket}")
        except Exception as e:
            logger.warning(f"S3 client initialization failed or unconfigured: {e}. Falling back to in-memory store.")
            self.use_s3 = False

    def put_json(self, key: str, data: Any) -> bool:
        """Store JSON object under key in S3 (or memory fallback)."""
        # Always update memory cache first
        self._memory_store[key] = data

        if not self.use_s3 or not self.client:
            return True

        try:
            logger.info(f"S3 PUT key: {key}")
            body = json.dumps(data, indent=2, ensure_ascii=False)
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body.encode("utf-8"),
                ContentType="application/json",
            )
            return True
        except (ClientError, BotoCoreError, Exception) as e:
            logger.error(f"S3 put_json failed for {key}: {e}. Retaining in memory store.")
            return True

    def get_json(self, key: str) -> Optional[Any]:
        """Fetch JSON object by key from S3 (or memory fallback)."""
        if self.use_s3 and self.client:
            try:
                logger.info(f"S3 GET key: {key}")
                response = self.client.get_object(Bucket=self.bucket, Key=key)
                content = response["Body"].read().decode("utf-8")
                parsed = json.loads(content)
                self._memory_store[key] = parsed
                return parsed
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                if error_code in ("NoSuchKey", "404"):
                    logger.info(f"S3 key not found: {key}")
                    return self._memory_store.get(key)
                logger.error(f"S3 ClientError getting {key}: {e}")
            except Exception as e:
                logger.error(f"S3 get_json failed for {key}: {e}")

        return self._memory_store.get(key)

    def list_json(self, prefix: str) -> List[Any]:
        """List all JSON objects matching prefix from S3 (or memory fallback)."""
        results: List[Any] = []

        if self.use_s3 and self.client:
            try:
                logger.info(f"S3 LIST prefix: {prefix}")
                paginator = self.client.get_paginator("list_objects_v2")
                pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)

                s3_keys = []
                for page in pages:
                    for obj in page.get("Contents", []):
                        s3_keys.append(obj["Key"])

                if s3_keys:
                    for key in s3_keys:
                        val = self.get_json(key)
                        if val is not None:
                            results.append(val)
                    return results
            except Exception as e:
                logger.error(f"S3 list_json failed for prefix {prefix}: {e}")

        # Fallback to memory store
        for key, val in self._memory_store.items():
            if key.startswith(prefix) and val is not None:
                results.append(val)

        return results

    def delete_json(self, key: str) -> bool:
        """Delete JSON object by key from S3 (or memory fallback)."""
        if key in self._memory_store:
            del self._memory_store[key]

        if not self.use_s3 or not self.client:
            return True

        try:
            logger.info(f"S3 DELETE key: {key}")
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception as e:
            logger.error(f"S3 delete_json failed for {key}: {e}")
            return True

    def check_status(self) -> str:
        """Check S3 connectivity status for system status endpoint."""
        if not self.use_s3 or not self.client:
            return "in_memory_fallback"
        try:
            self.client.head_bucket(Bucket=self.bucket)
            return "connected"
        except Exception:
            return "in_memory_fallback"


s3_service = S3Service()
