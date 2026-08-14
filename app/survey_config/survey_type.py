from enum import Enum


class SurveyType(Enum):
    DEFAULT = "default"
    CENSUS = "census"
    NI_CENSUS = "census-nisra"
    NRS_CENSUS = "census-nrs"
