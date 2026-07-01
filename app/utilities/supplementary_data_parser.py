from typing import Any, Mapping, TypedDict

from marshmallow import INCLUDE, Schema, ValidationError, fields, validate, validates, validates_schema
from marshmallow.experimental.context import Context

from app.utilities.metadata_parser_v2 import VALIDATORS, StripWhitespaceMixin


class SupplementaryDataMetadataContext(TypedDict):
    dataset_id: str
    identifier: str
    survey_id: str
    sds_schema_version: str | None


SupplementaryDataMetadataSchemaContext = Context[SupplementaryDataMetadataContext]


class ItemsSchema(Schema):
    identifier: fields.Field = fields.Field(required=True)
    ITEM_IDENTIFIER_ERROR_MESSAGE = "Item {data_key} must be a non-empty string or non-negative integer"

    @validates("identifier")
    def validate_identifier(self, identifier: fields.Field, data_key: str) -> None:
        if not (isinstance(identifier, str) and identifier.strip()) and not (
            isinstance(identifier, int) and identifier >= 0
        ):
            raise ValidationError(self.ITEM_IDENTIFIER_ERROR_MESSAGE.format(data_key=data_key))


class ItemsData(Schema, StripWhitespaceMixin):
    pass


class SupplementaryData(Schema, StripWhitespaceMixin):
    SDS_IDENTIFIER_ERROR_MESSAGE = "Supplementary data did not return the specified Identifier"

    identifier = VALIDATORS["string"](validate=validate.Length(min=1))
    items = fields.Nested(ItemsData, required=False, unknown=INCLUDE)

    @validates_schema()
    def validate_identifier(self, data: Mapping, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        if data and data["identifier"] != SupplementaryDataMetadataSchemaContext.get()["identifier"]:
            raise ValidationError(self.SDS_IDENTIFIER_ERROR_MESSAGE)


class SupplementaryDataMetadataSchema(Schema, StripWhitespaceMixin):

    DATASET_ID_ERROR_MESSAGE = "Supplementary data did not return the specified Dataset ID"
    SURVEY_ID_ERROR_MESSAGE = "Supplementary data did not return the specified Survey ID"
    SDS_VERSION_ERROR_MESSAGE = (
        "The Supplementary Dataset Schema Version does not match the version set in the Questionnaire Schema"
    )

    dataset_id = VALIDATORS["uuid"]()
    survey_id = VALIDATORS["string"](validate=validate.Length(min=1))
    data = fields.Nested(
        SupplementaryData,
        required=True,
        unknown=INCLUDE,
        validate=validate.Length(min=1),
    )

    @validates_schema()
    def validate_payload(self, payload: Mapping, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        if payload:
            if payload["dataset_id"] != SupplementaryDataMetadataSchemaContext.get()["dataset_id"]:
                raise ValidationError(self.DATASET_ID_ERROR_MESSAGE)

            if payload["survey_id"] != SupplementaryDataMetadataSchemaContext.get()["survey_id"]:
                raise ValidationError(self.SURVEY_ID_ERROR_MESSAGE)

            if SupplementaryDataMetadataSchemaContext.get()["sds_schema_version"] and (
                payload["data"]["schema_version"] != SupplementaryDataMetadataSchemaContext.get()["sds_schema_version"]
            ):
                raise ValidationError(self.SDS_VERSION_ERROR_MESSAGE)


def validate_supplementary_data_v1(
    supplementary_data: Mapping,
    dataset_id: str,
    identifier: str,
    survey_id: str,
    sds_schema_version: str | None = None,
) -> dict[str, str | dict | int | list]:
    """Validate claims required for supplementary data"""
    supplementary_data_metadata_schema = SupplementaryDataMetadataSchema(unknown=INCLUDE)
    with SupplementaryDataMetadataSchemaContext(
        {
            "dataset_id": dataset_id,
            "identifier": identifier,
            "survey_id": survey_id,
            "sds_schema_version": sds_schema_version,
        }
    ):
        validated_supplementary_data = supplementary_data_metadata_schema.load(supplementary_data)
    if supplementary_data_items := supplementary_data.get("data", {}).get("items"):
        for key, values in supplementary_data_items.items():
            items = [ItemsSchema(unknown=INCLUDE).load(value) for value in values]
            validated_supplementary_data["data"]["items"][key] = items

    # Type ignore: the load method in the Marshmallow parent schema class doesn't have type hints for return
    return validated_supplementary_data  # type: ignore
