from copy import deepcopy

import pytest
from freezegun import freeze_time
from marshmallow import ValidationError

from app.utilities.metadata_parser_v2 import validate_questionnaire_claims, validate_runner_claims_v2
from tests.app.parser.conftest import get_metadata, get_metadata_full
from tests.app.views.handlers.conftest import metadata


def test_spaces_are_stripped_from_string_fields():
    metadata = get_metadata()
    metadata["collection_exercise_sid"] = "  stripped     "

    output = validate_runner_claims_v2(metadata)

    assert output["collection_exercise_sid"] == "stripped"


def test_empty_strings_are_not_valid():
    metadata = get_metadata()
    metadata["schema_name"] = ""

    with pytest.raises(ValidationError):
        validate_runner_claims_v2(metadata)

def test_uuid_deserialisation():
    metadata = get_metadata_full()

    claims = validate_runner_claims_v2(metadata)

    assert isinstance(claims["tx_id"], str)


def test_unknown_claims_are_not_deserialized():
    metadata = get_metadata_full()

    metadata["unknown_key"] = "some value"
    claims = validate_runner_claims_v2(metadata)
    assert "unknown_key" not in claims


def test_minimum_length_on_runner_metadata():
    metadata = get_metadata_full()

    validate_runner_claims_v2(metadata)

    metadata["collection_exercise_sid"] = ""
    with pytest.raises(ValidationError):
        validate_runner_claims_v2(metadata)


def test_no_schema_claim_invalid_v2():
    metadata = get_metadata_full()
    del metadata["schema_name"]

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims_v2(metadata)

    assert "None of schema_name, schema_url or schema have been set in metadata" in str(exc)


@pytest.mark.parametrize(
    "options",
    [
        {"schema_name": "test_name", "schema_url": "http://test.json"},
        {"schema_name": "test_name", "schema": {"survey": "test", "form_type": "H", "region_code": "GB-WLS"}},
        {"schema_name": "test_name", "schema_url": "http://test.json", "schema": {"survey": "test", "form_type": "H", "region_code": "GB-WLS"}},
        {"schema_url": "http://test.json", "schema": {"survey": "test", "form_type": "H", "region_code": "GB-WLS"}},
    ],
)
def test_multiple_schema_claims_invalid_v2(options):
    metadata = get_metadata_full()
    del metadata["schema_name"]

    metadata.update(options)
    provided = ", ".join(options)

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims_v2(metadata)

    assert (
        f"Only one of schema_name, schema_url or schema should be specified in metadata, but {provided} were provided"
        in str(exc)
    )


@pytest.mark.parametrize(
    "schema",
    [
        {"survey": "test", "form_type": "H"},
        {"survey": "test", "region_code": "GB-WLS"},
        {"form_type": "H", "region_code": "GB-WLS"},
    ],
)
def test_schema_selector_schema_missing_properties(schema):
    metadata = get_metadata_full()
    del metadata["schema_name"]
    metadata["schema"] = schema

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims_v2(metadata)

    assert "Missing data for required field" in str(exc)


def test_schema_selector_schema_invalid_form_type():
    metadata = get_metadata_full()
    del metadata["schema_name"]
    metadata["schema"] = {"survey": "test", "form_type": "INVALID", "region_code": "GB-WLS"}

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims_v2(metadata)

    assert "Must be one of: H, I, C." in str(exc)


def test_schema_selector_schema_invalid_region_code():
    metadata = get_metadata_full()
    del metadata["schema_name"]
    metadata["schema"] = {"survey": "test", "form_type": "H", "region_code": "INVALID"}

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims_v2(metadata)

    assert "String does not match expected pattern" in str(exc)


def test_validate_questionnaire_claims_does_not_change_metadata():
    metadata = get_metadata_full()
    questionnaire_metadata_requirements_full = [
        {"name": "user_id", "type": "string"},
        {"name": "period_id", "type": "string"},
        {"name": "ref_p_start_date", "type": "string"},
        {"name": "ref_p_end_date", "type": "string"},
        {"name": "account_service_url", "type": "url", "optional": True},
    ]

    metadata_copy = deepcopy(metadata)

    questionnaire_claims = metadata["survey_metadata"]

    validate_questionnaire_claims(questionnaire_claims, questionnaire_metadata_requirements_full)

    assert metadata == metadata_copy


def test_validate_questionnaire_claims_no_error_when_optional_field_not_passed():
    metadata = get_metadata_full()

    field_specification = [{"name": "optional_field", "type": "string", "optional": True}]

    validate_questionnaire_claims(metadata, field_specification)


def test_validate_questionnaire_claims_field_required_by_default():
    metadata = get_metadata_full()

    field_specification = [{"name": "required_field", "type": "string"}]

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(metadata, field_specification)


def test_validate_questionnaire_claims_minimum_length():
    metadata = get_metadata_full()

    field_specification = [{"name": "some_field", "type": "string", "min_length": 5}]

    questionnaire_claims = metadata["survey_metadata"]

    questionnaire_claims["some_field"] = "123456"

    validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "1"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_maximum_length():
    metadata = get_metadata_full()

    field_specification = [{"name": "some_field", "type": "string", "max_length": 5}]

    questionnaire_claims = metadata["survey_metadata"]

    questionnaire_claims["some_field"] = "1234"

    validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123456"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_min_and_max_length():
    metadata = get_metadata_full()

    field_specification = [{"name": "some_field", "type": "string", "min_length": 4, "max_length": 5}]

    questionnaire_claims = metadata["survey_metadata"]

    questionnaire_claims["some_field"] = "1234"

    validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123456"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_length_equals():
    metadata = get_metadata_full()

    field_specification = [{"name": "some_field", "type": "string", "length": 4}]

    questionnaire_claims = metadata["survey_metadata"]

    questionnaire_claims["some_field"] = "1234"

    validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123456"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_deserialisation_iso_8601_dates():
    """Runner cannot currently handle date objects in metadata"""
    metadata = get_metadata_full()

    field_specification = [{"name": "birthday", "type": "date"}]

    questionnaire_claims = metadata["survey_metadata"]

    questionnaire_claims["birthday"] = "2019-11-1"
    claims = validate_questionnaire_claims(questionnaire_claims, field_specification)

    assert isinstance(claims["birthday"], str)

