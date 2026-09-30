from typing import Mapping
from uuid import uuid4

from google.api_core.exceptions import Forbidden
from google.cloud import storage  # type: ignore
from structlog import get_logger

logger = get_logger()

ReceiptingMetadataType = Mapping[str, str]


class LogSubmitter:
    @staticmethod
    def send_message(message: str, tx_id: str, receipting_metadata: ReceiptingMetadataType) -> bool:
        logger.info("sending message")
        logger.info(
            "message payload",
            message=message,
            tx_id=tx_id,
            receipting_metadata=receipting_metadata,
        )

        return True


class GCSSubmitter:
    def __init__(self, bucket_name: str) -> None:
        client = storage.Client()
        self.bucket = client.get_bucket(bucket_name)

    def send_message(self, message: str, tx_id: str, receipting_metadata: ReceiptingMetadataType) -> bool:
        logger.info("sending message")

        blob = self.bucket.blob(tx_id)
        blob.metadata = receipting_metadata

        try:
            blob.upload_from_string(str(message).encode("utf8"))
        except Forbidden as e:
            # If an object exists then the GCS Client will attempt to delete the
            # existing object before reuploading. However, in an attempt to reduce
            # duplicate receipts, runner does not have a delete permission. The first
            # version of the object is acceptable as it is an extreme edge case for
            # two submissions to contain different response data.
            if "storage.objects.delete" not in e.message:
                raise

            logger.info("Questionnaire submission exists, ignoring delete operation error")
        return True


class GCSFeedbackSubmitter:
    def __init__(self, bucket_name: str) -> None:
        client = storage.Client()
        self.bucket = client.get_bucket(bucket_name)

    def upload(self, payload: str, receipting_metadata: ReceiptingMetadataType) -> bool:
        blob = self.bucket.blob(str(uuid4()))
        blob.metadata = receipting_metadata

        blob.upload_from_string(payload.encode("utf8"))

        return True


class LogFeedbackSubmitter:
    @staticmethod
    def upload(payload: str, metadata: ReceiptingMetadataType) -> bool:
        logger.info("uploading feedback")
        logger.info(
            "feedback message",
            payload=payload,
            receipting_metadata=metadata,
        )

        return True
