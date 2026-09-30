import pytest
from marshmallow import ValidationError

from app.utilities.metadata_parser import validate_questionnaire_claims, validate_runner_claims
from tests.app.parser.conftest import get_metadata


def test_spaces_are_stripped_from_string_fields():
    metadata = get_metadata()
    metadata["collection_exercise_sid"] = "  stripped     "

    output = validate_runner_claims(metadata)

    assert output["collection_exercise_sid"] == "stripped"


def test_empty_strings_are_not_valid():
    metadata = get_metadata()
    metadata["schema_name"] = ""

    with pytest.raises(ValidationError):
        validate_runner_claims(metadata)


def test_uuid_deserialisation():
    metadata = get_metadata()

    claims = validate_runner_claims(metadata)

    assert isinstance(claims["tx_id"], str)


def test_unknown_claims_are_not_deserialized():
    metadata = get_metadata()

    metadata["unknown_key"] = "some value"
    claims = validate_runner_claims(metadata)
    assert "unknown_key" not in claims


def test_minimum_length_on_runner_metadata():
    metadata = get_metadata()

    validate_runner_claims(metadata)

    metadata["collection_exercise_sid"] = ""
    with pytest.raises(ValidationError):
        validate_runner_claims(metadata)


def test_no_schema_claim_invalid():
    metadata = get_metadata()
    del metadata["schema_name"]

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims(metadata)

    assert "None of schema_name, schema_url or schema have been set in metadata" in str(exc)


@pytest.mark.parametrize(
    "options",
    [
        {
            "schema_name": "test_name",
            "schema_url": "http://test.json",
            "schema": {"survey": "test", "form_type": "H", "region_code": "GB-WLS"},
        },
        {"schema_name": "test_name", "schema_url": "http://test.json"},
        {"schema_name": "test_name", "schema": {"survey": "test", "form_type": "H", "region_code": "GB-WLS"}},
        {"schema_url": "http://test.json", "schema": {"survey": "test", "form_type": "H", "region_code": "GB-WLS"}},
    ],
)
def test_multiple_schema_claims_invalid(options):
    metadata = get_metadata()
    del metadata["schema_name"]

    metadata.update(options)
    provided = ", ".join(options)

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims(metadata)

    assert (
        f"Only one of schema_name, schema_url or schema should be specified in metadata, but {provided} were provided"
        in str(exc)
    )


@pytest.mark.parametrize(
    "survey, form_type, region_code, expected",
    [
        ("CENSUS", "H", "GB-ENG", "census_household_gb_eng"),
        ("CENSUS", "I", "GB-ENG", "census_individual_gb_eng"),
        ("CENSUS", "C", "GB-ENG", "census_communal_establishment_gb_eng"),
        ("CENSUS", "H", "GB-WLS", "census_household_gb_wls"),
        ("CENSUS", "H", "GB-NIR", "census_household_gb_nir"),
        ("X", "H", "GB-NIR", "x_household_gb_nir"),
    ],
)
def test_schema_selector_populates_schema_name(survey, form_type, region_code, expected):
    metadata = get_metadata()
    del metadata["schema_name"]
    metadata["schema"] = {"survey": survey, "form_type": form_type, "region_code": region_code}

    claims = validate_runner_claims(metadata)

    assert claims["schema_name"] == expected


@pytest.mark.parametrize(
    "schema",
    [
        {"survey": "test", "form_type": "H"},
        {"survey": "test", "region_code": "GB-WLS"},
        {"form_type": "H", "region_code": "GB-WLS"},
    ],
)
def test_schema_selector_schema_missing_properties(schema):
    metadata = get_metadata()
    del metadata["schema_name"]
    metadata["schema"] = schema

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims(metadata)

    assert "Missing data for required field" in str(exc)


def test_schema_selector_schema_invalid_form_type():
    metadata = get_metadata()
    del metadata["schema_name"]
    metadata["schema"] = {"survey": "test", "form_type": "INVALID", "region_code": "GB-WLS"}

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims(metadata)

    assert "Must be one of: H, I, C." in str(exc)


def test_schema_selector_schema_invalid_region_code():
    metadata = get_metadata()
    del metadata["schema_name"]
    metadata["schema"] = {"survey": "test", "form_type": "H", "region_code": "INVALID"}

    with pytest.raises(ValidationError) as exc:
        validate_runner_claims(metadata)

    assert "String does not match expected pattern" in str(exc)


def test_validate_questionnaire_claims_no_error_when_optional_field_not_passed():
    field_specification = [{"name": "optional_field", "type": "string", "optional": True}]
    questionnaire_claims = {}

    validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_field_required_by_default():
    field_specification = [{"name": "required_field", "type": "string"}]
    questionnaire_claims = {}

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_minimum_length():
    field_specification = [{"name": "some_field", "type": "string", "min_length": 5}]
    questionnaire_claims = {"some_field": "123456"}

    validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "1"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_maximum_length():
    field_specification = [{"name": "some_field", "type": "string", "max_length": 5}]
    questionnaire_claims = {"some_field": "1234"}

    validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123456"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_min_and_max_length():
    field_specification = [{"name": "some_field", "type": "string", "min_length": 4, "max_length": 5}]
    questionnaire_claims = {"some_field": "1234"}

    validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123456"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_length_equals():
    field_specification = [{"name": "some_field", "type": "string", "length": 4}]
    questionnaire_claims = {"some_field": "1234"}

    validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123456"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)

    questionnaire_claims["some_field"] = "123"

    with pytest.raises(ValidationError):
        validate_questionnaire_claims(questionnaire_claims, field_specification)


def test_validate_questionnaire_claims_deserialisation_iso_8601_dates():
    field_specification = [{"name": "birthday", "type": "date"}]
    questionnaire_claims = {"birthday": "2019-11-1"}

    claims = validate_questionnaire_claims(questionnaire_claims, field_specification)

    assert isinstance(claims["birthday"], str)
