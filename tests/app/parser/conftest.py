import uuid

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
