import pytest
from werkzeug.datastructures import ImmutableDict

from app.authentication.auth_payload_versions import AuthPayloadVersion
from app.data_models.metadata_proxy import MetadataProxy, SchemaSelector
from tests.app.views.handlers.conftest import region_code

METADATA_V2 = {
    "version": AuthPayloadVersion.V2.value,
    "response_id": "1",
    "account_service_url": "account_service_url",
    "tx_id": "tx_id",
    "collection_exercise_sid": "collection_exercise_sid",
    "case_id": "case_id",
    "response_expires_at": "2023-04-24T10:46:32+00:00",
    "schema": {
        "survey": "CENSUS",
        "form_type": "H",
        "region_code": "GB-ENG"
    },
}


@pytest.mark.parametrize(
    "resolved_metadata_proxy_value, metadata_var",
    (
        (
            MetadataProxy.from_dict(METADATA_V2)["case_id"],
            METADATA_V2["case_id"],
        ),
        (
            MetadataProxy.from_dict(METADATA_V2)["response_expires_at"],
            METADATA_V2["response_expires_at"],
        ),
        (MetadataProxy.from_dict(METADATA_V2)["non_existing"], None),
    ),
)
def test_metadata_proxy_returns_value_for_valid_key(resolved_metadata_proxy_value, metadata_var):
    assert resolved_metadata_proxy_value == metadata_var


def test_schema_selector():
    schema_selector = MetadataProxy.from_dict(METADATA_V2).schema
    assert isinstance(schema_selector, SchemaSelector)
    assert schema_selector.survey == "CENSUS"
    assert schema_selector.form_type == "H"
    assert schema_selector.region_code == "GB-ENG"
