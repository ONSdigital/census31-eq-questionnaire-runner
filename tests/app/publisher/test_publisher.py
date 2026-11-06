from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from app.publisher.exceptions import InvalidTopicId, PublicationFailed
from app.publisher.publisher import PubSubPublisher


def test_init_raises_value_error_when_google_auth_default_returns_no_project_id(mocker):
    mocker.patch("app.publisher.publisher.PublisherClient")
    mocker.patch(
        "app.publisher.publisher.google.auth.default", return_value=(mocker.Mock(universe_domain="test"), None)
    )

    with pytest.raises(ValueError, match="Google Cloud project ID is required to publish to Pub/Sub topics"):
        PubSubPublisher()


@pytest.mark.parametrize(
    "project_id, expected_project_id",
    [
        (None, "test-project-id"),
        ("", "test-project-id"),
        (" ", "test-project-id"),
        ("an-external-project-id", "an-external-project-id"),
        (" an-external-project-id ", "an-external-project-id"),
    ],
)
def test_publish_calls_publisher_client_with_expected_topic_path(publisher, mocker, project_id, expected_project_id):
    expected_topic_path = f"projects/{expected_project_id}/topics/a-valid-topic-id"

    mock_future = mocker.Mock()
    mock_future.result.return_value = "a-dummy-message-id"
    mocker.patch.object(publisher._client, "publish", return_value=mock_future)

    publisher.publish(
        "a-valid-topic-id",
        b"test-message",
        fulfilment_request_transaction_id=str(uuid4()),
        project_id=project_id,
    )

    publisher._client.publish.assert_called_once_with(expected_topic_path, b"test-message")


def test_publish_raises_invalid_topic_id_for_invalid_topic_name(publisher):
    with pytest.raises(InvalidTopicId, match="topic_id must be"):
        publisher.publish(
            "A_BAD-topic-id",
            b"test-message",
            fulfilment_request_transaction_id=str(uuid4()),
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
