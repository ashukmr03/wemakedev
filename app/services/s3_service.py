import json
import logging
from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings

logger = logging.getLogger("carecircle.s3")


def _has_valid_aws_credentials() -> bool:
    """Return True only when explicit AWS credentials are configured.

    boto3 silently falls back to environment variables, IAM roles, and
    instance metadata — but in a local dev environment those are almost
    never valid.  Requiring explicit credentials avoids ~2-second network
    timeouts on every S3 call and prevents misleading error logs.
    """
    return bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)


class S3Service:
    """S3 Persistence Layer with graceful in-memory fallback for offline/demo reliability."""

    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.use_s3 = False
        self.client = None
        self._memory_store: Dict[str, Any] = {}

        if not _has_valid_aws_credentials():
            logger.info(
                "No explicit AWS credentials configured. "
                "S3 persistence disabled — using in-memory store. "
                "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env to enable S3."
            )
            return

        try:
            self.client = boto3.client(
                "s3",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            # Verify the bucket is reachable before enabling S3 mode.
            self.client.head_bucket(Bucket=self.bucket)
            self.use_s3 = True
            logger.info(f"S3 connected — bucket: {self.bucket}")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "404":
                logger.warning(
                    f"S3 bucket '{self.bucket}' not found. "
                    "Falling back to in-memory store."
                )
            else:
                logger.warning(
                    f"S3 bucket check failed ({error_code}). Falling back to in-memory store."
                )
            self.client = None
        except (BotoCoreError, Exception) as e:
            logger.warning(f"S3 initialization failed: {e}. Falling back to in-memory store.")
            self.client = None

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def put_json(self, key: str, data: Any) -> bool:
        """Store JSON object under key in S3 (or memory fallback)."""
        self._memory_store[key] = data

        if not self.use_s3 or not self.client:
            return True

        try:
            body = json.dumps(data, indent=2, ensure_ascii=False)
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body.encode("utf-8"),
                ContentType="application/json",
            )
            return True
        except (ClientError, BotoCoreError, Exception) as e:
            logger.error(f"S3 put_json failed for {key}: {e}. Data retained in memory.")
            return True

    def get_json(self, key: str) -> Optional[Any]:
        """Fetch JSON object by key from S3 (or memory fallback)."""
        if self.use_s3 and self.client:
            try:
                response = self.client.get_object(Bucket=self.bucket, Key=key)
                content = response["Body"].read().decode("utf-8")
                parsed = json.loads(content)
                self._memory_store[key] = parsed
                return parsed
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                if error_code in ("NoSuchKey", "404"):
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
