from enum import Enum


class SurveyType(Enum):
    DEFAULT = "default"
    CENSUS = "census"
    NI_CENSUS = "ni-census"
    NRS_CENSUS = "nrs-census"
