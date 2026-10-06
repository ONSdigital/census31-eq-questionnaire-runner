from dataclasses import dataclass, field
from typing import Iterable, Mapping, MutableMapping

from flask_babel import lazy_gettext

from app.settings import ACCOUNT_SERVICE_BASE_URL, CDN_CENSUS_ASSETS_PATH, CDN_URL, ONS_URL, ONS_URL_CY
from app.survey_config.link import Link
from app.survey_config.survey_config import SurveyConfig

CENSUS_ASSETS_BASE_URL = f"{CDN_URL.rstrip('/')}/{CDN_CENSUS_ASSETS_PATH.strip('/')}"


@dataclass
class CensusSurveyConfig(
    SurveyConfig,
):
    base_url: str = ACCOUNT_SERVICE_BASE_URL
    survey_title: str = lazy_gettext("ONS Census")
    title_logo: str = f"{CENSUS_ASSETS_BASE_URL}/images/census-logo.svg"
    css_override: str = f"{CENSUS_ASSETS_BASE_URL}/css/census.css"
    footer_links: Iterable[MutableMapping] = field(default_factory=list)
    footer_legal_links: Iterable[Mapping] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.language_code == "cy":
            self.title_logo = f"{CENSUS_ASSETS_BASE_URL}/images/census-logo-cy-small.svg"

        upstream_base_url = f"{self.base_url}/{self.language_code}"
        ons_url = ONS_URL_CY if self.language_code == "cy" else ONS_URL

        if not self.account_service_log_out_url:
            self.account_service_log_out_url: str = f"{upstream_base_url}/start/"

        self.cookie_settings_url: str = f"{upstream_base_url}/cookies/"
        self.privacy_and_data_protection_url: str = f"{upstream_base_url}/privacy-and-data-protection/"

        self.contact_us_url: str = f"{ons_url}/aboutus/contactus/surveyenquiries/"
        self.accessibility_url: str = f"{ons_url}/help/accessibility/"
        self.what_we_do_url: str = f"{ons_url}/aboutus/whatwedo/"

    def get_footer_links(self, cookie_has_theme: bool) -> list[dict]:
        links = [Link(lazy_gettext("What we do"), self.what_we_do_url).as_dict()]

        if cookie_has_theme:
            links.append(Link(lazy_gettext("Contact us"), self.contact_us_url).as_dict())

        links.append(
            Link(
                lazy_gettext("Accessibility"),
                self.accessibility_url,
            ).as_dict()
        )

        return links

    def get_footer_legal_links(self, cookie_has_theme: bool) -> list[dict] | None:
        if cookie_has_theme:
            return [
                Link(lazy_gettext("Cookies"), self.cookie_settings_url).as_dict(),
                Link(
                    lazy_gettext("Privacy and data protection"),
                    self.privacy_and_data_protection_url,
                ).as_dict(),
            ]

        return None


@dataclass
class NISRACensusSurveyConfig(CensusSurveyConfig):
    masthead_logo: str = f"{CENSUS_ASSETS_BASE_URL}/images/nisra-logo.svg"
    footer_logo: str = f"{CENSUS_ASSETS_BASE_URL}/images/nisra-footer-logo.svg"


@dataclass
class NRSCensusSurveyConfig(CensusSurveyConfig):
    masthead_logo: str = f"{CENSUS_ASSETS_BASE_URL}/images/nrs-logo.svg"
    footer_logo: str = f"{CENSUS_ASSETS_BASE_URL}/images/nrs-footer-logo.svg"
    css_override: str = f"{CENSUS_ASSETS_BASE_URL}/css/nrs-census.css"
