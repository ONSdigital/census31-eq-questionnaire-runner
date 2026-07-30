from datetime import datetime, timezone

from freezegun import freeze_time

from app.authentication.auth_payload_versions import AuthPayloadVersion
from app.questionnaire.questionnaire_schema import DEFAULT_LANGUAGE_CODE
from app.settings import CENSUS_PERIOD_ID
from app.views.handlers.feedback import FeedbackPayloadV2
from tests.app.views.handlers.conftest import (
    case_id,
    case_type,
    channel,
    collection_exercise_sid,
    data_version,
    display_address,
    feedback_count,
    feedback_text,
    feedback_type,
    language_code,
    questionnaire_id,
    ru_ref,
    schema_name,
    started_at,
    tx_id,
    user_id,
)


@freeze_time(datetime.now(tz=timezone.utc).isoformat())
def test_feedback_payload(session_data_feedback, schema_feedback, metadata, response_metadata):
    feedback_payload = FeedbackPayloadV2(
        metadata=metadata,
        response_metadata=response_metadata,
        schema=schema_feedback,
        case_id=case_id,
        submission_language_code=language_code,
        feedback_count=session_data_feedback.feedback_count,
        feedback_text=feedback_text,
        feedback_type=feedback_type,
    )

    expected_payload = {
        "case_id": case_id,
        "channel": channel,
        "collection_exercise_sid": collection_exercise_sid,
        "data": {
            "feedback_count": str(feedback_count),
            "feedback_text": feedback_text,
            "feedback_type": feedback_type,
        },
        "data_version": data_version,
        "flushed": False,
        "launch_language_code": "en",
        "origin": "uk.gov.ons.edc.eq",
        "period_id": CENSUS_PERIOD_ID,
        "schema_name": schema_name,
        "schema": metadata.schema.to_dict(),
        "started_at": started_at,
        "submission_language_code": language_code,
        "submitted_at": datetime.now(tz=timezone.utc).isoformat(),
        "survey_metadata": {
            "user_id": user_id,
            "ru_ref": ru_ref,
            "display_address": display_address,
            "questionnaire_id": questionnaire_id,
            "case_type": case_type,
        },
        "tx_id": tx_id,
        "type": "uk.gov.ons.edc.eq:feedback",
        "version": AuthPayloadVersion.V2.value,
    }

    assert expected_payload == feedback_payload()


def test_submission_language_code_uses_default_language_when_session_language_none(
    session_data_feedback, schema_feedback, metadata, response_metadata
):
    feedback_payload = FeedbackPayloadV2(
        metadata=metadata,
        response_metadata=response_metadata,
        schema=schema_feedback,
        case_id=case_id,
        submission_language_code=None,
        feedback_count=session_data_feedback.feedback_count,
        feedback_text=feedback_text,
        feedback_type=feedback_type,
    )

    assert feedback_payload()["submission_language_code"] == DEFAULT_LANGUAGE_CODE
