import uuid

import pytest

from app.authentication.auth_payload_versions import AuthPayloadVersion

def get_metadata():
    """Generate the set of top-level claims required for runner to function"""
    return {
        "tx_id": str(uuid.uuid4()),
        "jti": str(uuid.uuid4()),
        "schema_name": "2_a",
        "collection_exercise_sid": "test-sid",
        "response_id": str(uuid.uuid4()),
        "account_service_url": "https://ras.ons.gov.uk",
        "case_id": str(uuid.uuid4()),
        "version": AuthPayloadVersion.V2.value,
    }

def get_metadata_full():
    """Generate a full set claims including survey_metadata"""
    metadata = get_metadata()
    metadata["survey_metadata"] = {
        "user_id": "1",
        "period_id": "3",
        "ref_p_start_date": "2016-02-02",
        "ref_p_end_date": "2016-03-03",
        "ru_name": "Apple",
        "return_by": "2016-07-07",
        "case_ref": "1000000000000001",
        "ru_ref": "12345678901A",
        "form_type": "I",
    }
    return metadata
