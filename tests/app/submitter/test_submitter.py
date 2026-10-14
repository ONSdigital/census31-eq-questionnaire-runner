import pytest
from google.api_core.exceptions import Forbidden
from google.cloud.storage import Blob

from app.submitter import GCSFeedbackSubmitter, GCSSubmitter
from app.utilities.json import json_dumps


@pytest.fixture
def gcs_blob_create_forbidden(mocker):
    blob = Blob(name="test-blob", bucket=mocker.Mock())
    blob.upload_from_string = mocker.Mock(side_effect=Forbidden("storage.objects.create"))
    return blob


@pytest.fixture
def gcs_blob_delete_forbidden(mocker):
    blob = Blob(name="test-blob", bucket=mocker.Mock())
    blob.upload_from_string = mocker.Mock(side_effect=Forbidden("storage.objects.delete"))
    return blob


def test_gcs_submitter_sends_message(patch_gcs_client):
    gcs_submitter = GCSSubmitter(bucket_name="test_bucket")
    # When
    published = gcs_submitter.send_message(
        message=json_dumps({"some-data": "some-value"}),
        tx_id="123",
        receipting_metadata={},
    )

    # Then
    bucket = patch_gcs_client.return_value.get_bucket.return_value
    blob = bucket.blob.return_value
    assert isinstance(blob.metadata, dict)

    blob_name = bucket.blob.call_args[0][0]
    assert blob_name == "123"

    blob_contents = blob.upload_from_string.call_args[0][0]
    assert blob_contents == b'{"some-data": "some-value"}'

    assert published is True


def test_gcs_submitter_adds_metadata_when_sends_message(patch_gcs_client):
    gcs_submitter = GCSSubmitter(bucket_name="test_bucket")
    # When
    gcs_submitter.send_message(
        message="test_data",
        tx_id="123",
        receipting_metadata={"tx_id": "123", "case_id": "456"},
    )

    # Then
    bucket = patch_gcs_client.return_value.get_bucket.return_value
    blob = bucket.blob.return_value

    assert blob.metadata == {
        "tx_id": "123",
        "case_id": "456",
    }


def test_gcs_submitter_retries_transient_errors(patch_gcs_client, gcs_blob_with_retry):
    # Given
    gcs_submitter = GCSSubmitter(bucket_name="test_bucket")

    # When
    bucket = patch_gcs_client.return_value.get_bucket.return_value
    bucket.blob.return_value = gcs_blob_with_retry
    successful = gcs_submitter.send_message(message="some message", tx_id="123", receipting_metadata={})

    # Then the call count should be two since we have 2 side effects,
    # the 1st request returns a 503 and second request returns a 200.
    assert gcs_blob_with_retry._get_transport().request.call_count == 2
    assert successful is True


def test_double_submission_passes_when_delete_operation_error(patch_gcs_client, gcs_blob_delete_forbidden):
    # Given
    gcs_submitter = GCSSubmitter(bucket_name="test_bucket")

    # When
    bucket = patch_gcs_client.return_value.get_bucket.return_value
    bucket.blob.return_value = gcs_blob_delete_forbidden
    published = gcs_submitter.send_message(message="test_data", tx_id="123", receipting_metadata={})
    # Then
    assert published


def test_double_submission_is_forbidden_when_not_delete_operation_error(patch_gcs_client, gcs_blob_create_forbidden):
    # Given
    gcs_submitter = GCSSubmitter(bucket_name="test_bucket")

    # When
    bucket = patch_gcs_client.return_value.get_bucket.return_value
    bucket.blob.return_value = gcs_blob_create_forbidden

    # Then
    with pytest.raises(Forbidden):
        gcs_submitter.send_message(message="test_data", tx_id="123", receipting_metadata={})


def test_gcs_feedback_submitter_uploads_feedback(patch_gcs_client):
    # Given
    feedback = GCSFeedbackSubmitter(bucket_name="feedback")

    payload = json_dumps({"some-data": "some-value"})

    # When
    feedback_upload = feedback.upload(payload=payload, receipting_metadata={})

    # Then
    bucket = patch_gcs_client.return_value.get_bucket.return_value
    blob = bucket.blob.return_value

    blob_contents = blob.upload_from_string.call_args[0][0]

    assert blob_contents == b'{"some-data": "some-value"}'
    assert feedback_upload is True


def test_gcs_feedback_submitter_adds_metadata_when_set(
    patch_gcs_client,
):
    gcs_submitter = GCSFeedbackSubmitter(bucket_name="test_bucket")

    # When
    gcs_submitter.upload(
        payload=json_dumps({"some-data": "some-value"}),
        receipting_metadata={"tx_id": "123", "case_id": "456", "questionnaire_id": "1"},
    )

    # Then
    bucket = patch_gcs_client.return_value.get_bucket.return_value
    blob = bucket.blob.return_value

    assert blob.metadata == {
        "tx_id": "123",
        "case_id": "456",
        "questionnaire_id": "1",
    }


def test_gcs_feedback_submitter_retries_transient_errors(patch_gcs_client, gcs_blob_with_retry):
    # Given
    gcs_submitter = GCSFeedbackSubmitter(bucket_name="test_bucket")

    # When
    bucket = patch_gcs_client.return_value.get_bucket.return_value
    bucket.blob.return_value = gcs_blob_with_retry
    successful = gcs_submitter.upload(payload=json_dumps({"some-data": "some-value"}), receipting_metadata={})

    # Then the call count should be two since we have 2 side effects,
    # the 1st request returns a 503 and second request returns a 200.
    assert gcs_blob_with_retry._get_transport().request.call_count == 2
    assert successful is True
