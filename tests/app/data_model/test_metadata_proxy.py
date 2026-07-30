from app.authentication.auth_payload_versions import AuthPayloadVersion
from app.data_models.metadata_proxy import MetadataProxy, SchemaSelector

METADATA = {
    "version": AuthPayloadVersion.V2.value,
    "response_id": "1",
    "account_service_url": "account_service_url",
    "tx_id": "tx_id",
    "collection_exercise_sid": "collection_exercise_sid",
    "case_id": "case_id",
    "schema": {"survey": "CENSUS", "form_type": "H", "region_code": "GB-ENG"},
}


def test_metadata_proxy_returns_value_for_valid_key():
    metadata_proxy = MetadataProxy.from_dict(METADATA)
    assert metadata_proxy.version == AuthPayloadVersion(METADATA["version"])
    assert metadata_proxy.response_id == METADATA["response_id"]
    assert metadata_proxy.account_service_url == METADATA["account_service_url"]
    assert metadata_proxy.tx_id == METADATA["tx_id"]
    assert metadata_proxy.collection_exercise_sid == METADATA["collection_exercise_sid"]
    assert metadata_proxy.case_id == METADATA["case_id"]


def test_schema_selector():
    schema_selector = MetadataProxy.from_dict(METADATA).schema
    assert isinstance(schema_selector, SchemaSelector)
    assert schema_selector.survey == METADATA["schema"]["survey"]
    assert schema_selector.form_type == METADATA["schema"]["form_type"]
    assert schema_selector.region_code == METADATA["schema"]["region_code"]
