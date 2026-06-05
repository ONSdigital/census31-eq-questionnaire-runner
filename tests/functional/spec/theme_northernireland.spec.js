import RadioPage from "../generated_pages/theme_northernireland/radio.page";
import { normalizeHtml, verifyUrlContains } from "../helpers";

describe("Theme Northern Ireland", () => {
  describe("Given I launch a Northern Ireland themed questionnaire", () => {
    before(async () => {
      await browser.openQuestionnaire("test_theme_northernireland.json");
    });

    it("When I navigate to the radio page, Then I should see Northern Ireland theme content", async () => {
      await verifyUrlContains(RadioPage.pageName);
      await expect(normalizeHtml(await $("#finance-ni-logo-alt").getHTML())).toContain("Northern Ireland Department of Finance logo");
    });
  });
});
