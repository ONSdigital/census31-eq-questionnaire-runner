from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from werkzeug.datastructures import ImmutableDict

from app.authentication.auth_payload_versions import AuthPayloadVersion
from app.utilities.make_immutable import make_immutable


class NoMetadataException(Exception):
    pass


# "version" is excluded here as it is handled independently
TOP_LEVEL_METADATA_KEYS = [
    "tx_id",
    "account_service_url",
    "case_id",
    "collection_exercise_sid",
    "response_id",
    "response_expires_at",
    "language_code",
    "schema_name",
    "schema_url",
    "channel",
    "roles",
]


@dataclass(frozen=True)
class SchemaSelector:
    survey: str
    form_type: str
    region_code: str


@dataclass(frozen=True)
class MetadataProxy:
    tx_id: str
    account_service_url: str
    case_id: str
    collection_exercise_sid: str
    response_id: str
    response_expires_at: datetime
    survey_metadata: ImmutableDict | None = None
    schema_url: str | None = None
    schema_name: str | None = None
    schema: SchemaSelector | None = None
    language_code: str | None = None
    channel: str | None = None
    version: AuthPayloadVersion | None = None
    roles: list | None = None

    def __getitem__(self, key: str) -> Any | None:
        if self.survey_metadata and key in self.survey_metadata.data:
            return self.survey_metadata[key]

        return getattr(self, key, None)

    @classmethod
    def from_dict(cls, metadata: Mapping) -> MetadataProxy:
        _metadata = deepcopy(dict(metadata))
        version = AuthPayloadVersion(_metadata.pop("version")) if "version" in _metadata else None

        schema = None
        if serialized_schema := cls.serialize(_metadata.pop("schema", {})):
            schema = SchemaSelector(**serialized_schema)

        top_level_data = {key: _metadata.pop(key, None) for key in TOP_LEVEL_METADATA_KEYS}

        return cls(
            **top_level_data,
            version=version,
            schema=schema,
        )

    @classmethod
    def serialize(cls, data: Any) -> Any:
        return make_immutable(data)
