from enum import Enum


class SurveyType(Enum):
    DEFAULT = "default"
    CENSUS = "census"
    CENSUS_NISRA = "census-nisra"
    CENSUS_NRS = "census-nrs"
