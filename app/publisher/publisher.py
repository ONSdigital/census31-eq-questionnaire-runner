import re
from abc import ABC, abstractmethod

import google.auth
from google.cloud.pubsub import PublisherClient
from google.cloud.pubsub_v1.futures import Future
from structlog import get_logger

from app.publisher.exceptions import InvalidTopicId, PublicationFailed

logger = get_logger(__name__)

TOPIC_NAME_PATTERN = re.compile(r"^(?!goog)[a-z][a-z-]{2,254}$")


class Publisher(ABC):
    @abstractmethod
    def publish(
        self,
        topic_id: str,
        message: bytes,
        fulfilment_request_transaction_id: str,
        project_id: str | None = None,
    ) -> None:
        pass  # pragma: no cover


class PubSubPublisher(Publisher):
    def __init__(self) -> None:
        self._client = PublisherClient()
        _, project_id = google.auth.default()
        if not project_id:
            error_message = "Google Cloud project ID is required to publish to Pub/Sub topics"
            raise ValueError(error_message)

        self._project_id = project_id

    def _get_topic_path(self, topic_id: str, project_id: str | None = None) -> str:
        resolved_project_id = (project_id or "").strip() or self._project_id
        if TOPIC_NAME_PATTERN.match(topic_id):
            return f"projects/{resolved_project_id}/topics/{topic_id}"

        error_message = "topic_id must be a lowercase hyphenated topic name"
        raise InvalidTopicId(error_message)

    def publish(
        self,
        topic_id: str,
        message: bytes,
        fulfilment_request_transaction_id: str,
        project_id: str | None = None,
    ) -> None:
        topic_path = self._get_topic_path(topic_id=topic_id, project_id=project_id)
        logger.info("publishing message", topic_path=topic_path)
        response: Future = self._client.publish(topic_path, message)
        try:
            # Resolve the future
            message_id = response.result()
            logger.info(  # pragma: no cover
                "message published successfully",
                topic_path=topic_path,
                message_id=message_id,
                fulfilment_request_transaction_id=fulfilment_request_transaction_id,
            )
        except Exception as exc:
            logger.exception(
                "message publication failed",
                topic_path=topic_path,
            )
            raise PublicationFailed(exc) from exc


class LogPublisher(Publisher):
    def publish(
        self,
        topic_id: str,
        message: bytes,
        fulfilment_request_transaction_id: str,
        project_id: str | None = None,
    ) -> None:
        logger.info(
            "publishing message",
            topic_project_id=project_id,
            topic_id=topic_id,
            message=message,
            fulfilment_request_transaction_id=fulfilment_request_transaction_id,
        )
