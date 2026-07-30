from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from freezegun import freeze_time

from app.authentication.auth_payload_versions import AuthPayloadVersion
from app.data_models import QuestionnaireStore
from app.data_models.data_stores import DataStores
from app.data_models.metadata_proxy import MetadataProxy
from app.data_models.session_data import SessionData
from app.data_models.session_store import SessionStore
from app.questionnaire import QuestionnaireSchema

time_to_freeze = datetime.now(timezone.utc).replace(second=0, microsecond=0)
tx_id = "tx_id"
response_id = "1234567890123456"
ru_ref = "uprn:00001"
user_id = "789473423"
questionnaire_id = "1234567890"
schema_name = "1_0000"
feedback_count = 1
display_address = "68 Abingdon Road, Goathill"
collection_exercise_sid = "ce_sid"
case_id = "case_id"
case_type = "HH"
data_version = "0.0.1"
feedback_type = "Feedback type"
feedback_text = "Feedback text"
started_at = str(datetime.now(tz=timezone.utc).isoformat())
language_code = "cy"
channel = "RH"
region_code = "GB_WLS"


@pytest.fixture
@freeze_time(time_to_freeze)
def session_data():
    return SessionData(
        language_code="cy",
    )


@pytest.fixture
def confirmation_email_fulfilment_schema():
    return QuestionnaireSchema(
        {
            "form_type": "H",
            "region_code": "GB-WLS",
            "submission": {"confirmation_email": True},
        }
    )


@pytest.fixture
def language():
    return "en"


@pytest.fixture
def schema():
    return QuestionnaireSchema(
        {
            "post_submission": {"view_response": True},
            "title": "Test schema - View Submitted Response",
        }
    )


@pytest.fixture
def storage():
    return Mock()


def set_storage_data(
    storage_,
    raw_data="{}",
    version=1,
    submitted_at=None,
):
    storage_.get_user_data = Mock(return_value=(raw_data, version, collection_exercise_sid, submitted_at))


@pytest.fixture
def session_data_feedback():
    return SessionData(
        language_code=language_code,
        feedback_count=feedback_count,
    )


@pytest.fixture
def schema_feedback():
    return QuestionnaireSchema({"survey_id": "123", "data_version": data_version})


@pytest.fixture
def metadata():
    return MetadataProxy.from_dict(
        {
            "version": AuthPayloadVersion.V2,
            "tx_id": tx_id,
            "case_id": case_id,
            "schema_name": schema_name,
            "schema": {
                "survey": "CENSUS",
                "form_type": "H",
                "region_code": "GB-WLS",
            },
            "collection_exercise_sid": collection_exercise_sid,
            "response_id": response_id,
            "channel": channel,
            "account_service_url": "account_service_url",
            "survey_metadata": {
                "user_id": user_id,
                "display_address": display_address,
                "questionnaire_id": questionnaire_id,
                "case_type": case_type,
                "ru_ref": ru_ref,
            },
        }
    )


@pytest.fixture
def response_metadata():
    return {
        "started_at": started_at,
    }


@pytest.fixture
def submission_payload_expires_at():
    return datetime.now(timezone.utc) + timedelta(seconds=5)


@pytest.fixture
def submission_payload_session_data():
    return SessionData(
        language_code="cy",
    )


@pytest.fixture
def submission_payload_session_store(
    submission_payload_session_data,
    submission_payload_expires_at,
):
    return SessionStore("user_ik", "pepper", "eq_session_id").create(
        "eq_session_id",
        "user_id",
        submission_payload_session_data,
        submission_payload_expires_at,
    )


@pytest.fixture
def mock_questionnaire_store(mocker, metadata):
    storage_ = mocker.Mock()
    storage_.get_user_data = mocker.Mock(return_value=("{}", "ce_id", 1, None))
    questionnaire_store = QuestionnaireStore(storage_)
    questionnaire_store.data_stores = DataStores(
        metadata=metadata,
    )
    return questionnaire_store


@pytest.fixture
def mock_questionnaire_store_v2(mocker, metadata):
    storage_ = mocker.Mock()
    storage_.get_user_data = mocker.Mock(return_value=("{}", "ce_id", 1, None))
    questionnaire_store = QuestionnaireStore(storage_)
    questionnaire_store.data_stores = DataStores(
        metadata=metadata,
    )
    return questionnaire_store
