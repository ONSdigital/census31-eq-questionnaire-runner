import functools
from typing import Any, Callable, Iterable, Mapping, MutableMapping

from marshmallow import EXCLUDE, INCLUDE, Schema, ValidationError, fields, pre_load, validate, validates_schema
from structlog import get_logger

from app.authentication.auth_payload_versions import AuthPayloadVersion
from app.utilities.metadata_validators import DateString, RegionCode, UUIDString

logger = get_logger()

VALIDATORS: Mapping[str, Callable] = {
    "date": functools.partial(DateString, format="%Y-%m-%d", required=True),
    "uuid": functools.partial(UUIDString, required=True),
    "boolean": functools.partial(fields.Boolean, required=True),
    "string": functools.partial(fields.String, required=True),
    "url": functools.partial(fields.Url, required=True),
}


class StripWhitespaceMixin:
    @pre_load()
    def strip_whitespace(self, items: MutableMapping, **kwargs: Any) -> MutableMapping:
        for key, value in items.items():
            if isinstance(value, str):
                items[key] = value.strip()
        return items


class Data(Schema, StripWhitespaceMixin):
    pass


class SchemaSelector(Schema, StripWhitespaceMixin):
    survey = fields.String(required=True)
    form_type = fields.String(required=True, validate=validate.OneOf(["H", "I", "C"]))
    region_code = fields.String(required=True, validate=RegionCode())


class RunnerMetadataSchema(Schema, StripWhitespaceMixin):
    """Metadata which is required for the operation of runner itself"""

    METADATA_OPTION_ERROR_MESSAGE = "None of schema_name, schema_url or schema have been set in metadata"

    jti = UUIDString(required=True)
    tx_id = UUIDString(required=True)
    case_id = UUIDString(required=True)
    collection_exercise_sid = fields.String(required=True, validate=validate.Length(min=1))
    version = fields.String(required=True, validate=validate.OneOf([AuthPayloadVersion.V2.value]))
    response_id = fields.String(required=True)
    account_service_url = fields.Url(required=True)
    channel = fields.String(required=False, validate=validate.Length(min=1))
    language_code = fields.String(required=False)
    roles = fields.List(fields.String(), required=False)

    schema_name = fields.String(required=False)
    schema_url = fields.Url(required=False)
    schema = fields.Nested(SchemaSelector, required=False)

    survey_metadata = fields.Nested(Data, unknown=INCLUDE, validate=validate.Length(min=1))

    @validates_schema
    def validate_schema_options(self, data: Mapping, **kwargs: Any) -> None:
        if data:
            options = [option for option in ["schema_name", "schema_url", "schema"] if data.get(option)]
            if len(options) == 0:
                raise ValidationError(self.METADATA_OPTION_ERROR_MESSAGE)
            if len(options) > 1:
                metadata_combination_error_message = (
                    "Only one of schema_name, schema_url or schema should be specified "
                    f"in metadata, but {', '.join(options)} were provided"
                )
                raise ValidationError(metadata_combination_error_message)


def validate_questionnaire_claims(
    claims: Mapping,
    questionnaire_specific_metadata: Iterable[Mapping],
    unknown: str = EXCLUDE,
) -> dict:
    """Validate any survey specific claims required for a questionnaire"""
    dynamic_fields: dict[str, fields.String | DateString] = {}

    for metadata_field in questionnaire_specific_metadata:
        field_arguments: dict[str, bool] = {}
        validators: list[validate.Validator] = []

        if metadata_field.get("optional"):
            field_arguments["required"] = False

        if any(length_limit in metadata_field for length_limit in ("min_length", "max_length", "length")):
            validators.append(
                validate.Length(
                    min=metadata_field.get("min_length"),
                    max=metadata_field.get("max_length"),
                    equal=metadata_field.get("length"),
                )
            )

        dynamic_fields[metadata_field["name"]] = VALIDATORS[metadata_field["type"]](
            validate=validators, **field_arguments
        )

    questionnaire_metadata_schema = type("QuestionnaireMetadataSchema", (Schema, StripWhitespaceMixin), dynamic_fields)(
        unknown=unknown
    )

    # The load method performs validation.
    # Type ignore: the load method in the Marshmallow parent schema class doesn't have type hints for return
    return questionnaire_metadata_schema.load(claims)  # type: ignore


def validate_runner_claims(claims: Mapping) -> dict:
    """Validate claims required for runner to function"""
    runner_metadata_schema = RunnerMetadataSchema(unknown=EXCLUDE)
    # Type ignore: the load method in the Marshmallow parent schema class doesn't have type hints for return
    return runner_metadata_schema.load(claims)  # type: ignore
