from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from google.cloud.pubsub_v1.open_telemetry.publish_message_wrapper import PublishMessageWrapper
from google.pubsub_v1.types.pubsub import PubsubMessage

from app.publisher.exceptions import InvalidTopicId, PublicationFailed
from app.publisher.publisher import PubSubPublisher


def test_publish(publisher, mocker):
    topic_id = "test-topic-id"
    topic_path = f"projects/test-project-id/topics/{topic_id}"

    future = mocker.sentinel.future
    future.add_done_callback = mocker.Mock(spec=["__call__"])

    # Use a mock in lieu of the actual batch class.
    batch = mocker.Mock(spec=publisher._client._batch_class)

    # Set the mock up to accepts the message.
    batch.publish.side_effect = (future,)

    publisher._client._set_batch(topic_path, batch)

    # Publish message.
    future = publisher._publish(topic_id, b"test-message", project_id="test-project-id")
    assert future is mocker.sentinel.future

    # Check mock.
    batch.publish.assert_has_calls([mocker.call(PublishMessageWrapper(PubsubMessage({"data": b"test-message"})))])


def test_init_raises_value_error_when_google_auth_default_returns_no_project_id(mocker):
    mocker.patch("app.publisher.publisher.PublisherClient")
    mocker.patch(
        "app.publisher.publisher.google.auth.default", return_value=(mocker.Mock(universe_domain="test"), None)
    )

    with pytest.raises(ValueError, match="Google Cloud project ID is required to publish to Pub/Sub topics"):
        PubSubPublisher()


def test_publish_uses_provided_project_id_when_constructing_topic_path(publisher, mocker):
    topic_id = "test-topic-id"
    topic_path = "projects/other-project/topics/test-topic-id"

    future = mocker.sentinel.future
    future.add_done_callback = mocker.Mock(spec=["__call__"])

    batch = mocker.Mock(spec=publisher._client._batch_class)
    batch.publish.side_effect = (future,)

    publisher._client._set_batch(topic_path, batch)

    response = publisher._publish(topic_id, b"test-message", project_id="other-project")

    assert response is mocker.sentinel.future
    batch.publish.assert_has_calls([mocker.call(PublishMessageWrapper(PubsubMessage({"data": b"test-message"})))])


def test_publish_uses_default_project_id_when_project_id_is_empty_string(publisher):
    with patch("app.publisher.publisher.PubSubPublisher._publish") as mock_publish:
        publisher.publish(
            "test-topic-id",
            b"test-message",
            fulfilment_request_transaction_id=str(uuid4()),
            project_id="",
        )

    mock_publish.assert_called_once_with("test-topic-id", b"test-message", project_id="test-project-id")


def test_get_topic_path_raises_invalid_topic_id_for_invalid_topic_name(publisher):
    with pytest.raises(InvalidTopicId, match="topic_id must be"):
        publisher._get_topic_path("A_BAD-topic-id", project_id="test-project-id")


def test_publish_raises_invalid_topic_id_for_malformed_fully_qualified_topic_path(publisher):
    with pytest.raises(InvalidTopicId, match="topic_id must be"):
        publisher._publish(
            "projects/test-project/THE_WRONG_KEY/good-topic", b"test-message", project_id="test-project-id"
        )


def test_resolving_message_raises_exception_on_error(publisher):
    mock_future = Mock()
    mock_future.result.side_effect = Exception()

    with (
        patch("app.publisher.publisher.PubSubPublisher._publish", return_value=mock_future),
        pytest.raises(PublicationFailed),
    ):
        publisher.publish(
            "test-topic-id",
            b"test-message",
            fulfilment_request_transaction_id=str(uuid4()),
        )
