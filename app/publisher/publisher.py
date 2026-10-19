import re
from abc import ABC, abstractmethod

import google.auth
from google.cloud.pubsub import PublisherClient
from google.cloud.pubsub_v1.futures import Future
from structlog import get_logger

from app.publisher.exceptions import InvalidTopicId, PublicationFailed

logger = get_logger(__name__)

FULLY_QUALIFIED_TOPIC_PATH_PATTERN = re.compile(r"^projects/(?P<project>.+?)/topics/(?P<topic>.+?)$")
TOPIC_NAME_PATTERN = re.compile(r"^(?!goog)[a-z][a-z-]{2,254}$")


class Publisher(ABC):
    @abstractmethod
    def publish(self, topic_id: str, message: bytes, fulfilment_request_transaction_id: str) -> None:
        pass  # pragma: no cover


class PubSubPublisher(Publisher):
    def __init__(self) -> None:
        self._client = PublisherClient()
        _, project_id = google.auth.default()
        if not project_id:
            error_message = "Google Cloud project ID is required to publish to Pub/Sub topics"
            raise ValueError(error_message)

        self._project_id = project_id

    def _publish(self, topic_id: str, message: bytes) -> Future:
        logger.info("publishing message", topic_id=topic_id)
        topic_path = self._get_topic_path(topic_id)
        response: Future = self._client.publish(topic_path, message)
        return response

    def _get_topic_path(self, topic_id: str) -> str:
        if FULLY_QUALIFIED_TOPIC_PATH_PATTERN.match(topic_id):
            return topic_id

        if TOPIC_NAME_PATTERN.match(topic_id):
            return self._client.topic_path(self._project_id, topic_id)

        error_message = (
            "topic_id must be either a fully qualified Pub/Sub topic path or a lowercase hyphenated topic name"
        )
        raise InvalidTopicId(error_message)

    def publish(self, topic_id: str, message: bytes, fulfilment_request_transaction_id: str) -> None:
        response = self._publish(topic_id, message)
        try:
            # Resolve the future
            message_id = response.result()
            logger.info(  # pragma: no cover
                "message published successfully",
                topic_id=topic_id,
                message_id=message_id,
                fulfilment_request_transaction_id=fulfilment_request_transaction_id,
            )
        except Exception as exc:
            logger.exception(
                "message publication failed",
                topic_id=topic_id,
            )
            raise PublicationFailed(exc) from exc


class LogPublisher(Publisher):
    def publish(self, topic_id: str, message: bytes, fulfilment_request_transaction_id: str) -> None:
        logger.info(
            "publishing message",
            topic_id=topic_id,
            message=message,
            fulfilment_request_transaction_id=fulfilment_request_transaction_id,
        )
