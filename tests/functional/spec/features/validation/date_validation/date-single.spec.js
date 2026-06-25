import DatePage from "../../../../generated_pages/date_validation_single/date-block.page";
import DatePeriodPage from "../../../../generated_pages/date_validation_single/date-range-block.page";
import SubmitPage from "../../../../generated_pages/date_validation_single/submit.page";
import { click, verifyUrlContains } from "../../../../helpers";
describe("Feature: Validation for single date periods", () => {
  beforeEach(async () => {
    await browser.openQuestionnaire("test_date_validation_single.json");
    await completeFirstDatePage();
  });

  describe("Given I enter a date before the minimum offset meta date", () => {
    it("When I continue, Then I should see a period validation error", async () => {
      await $(DatePeriodPage.dateRangeFromDay()).setValue(13);
      await $(DatePeriodPage.dateRangeFromMonth()).setValue(2);
      await $(DatePeriodPage.dateRangeFromYear()).setValue(2016);
      await click(DatePeriodPage.submit());

      await $(DatePeriodPage.dateRangeToDay()).setValue(3);
      await $(DatePeriodPage.dateRangeToMonth()).setValue(3);
      await $(DatePeriodPage.dateRangeToYear()).setValue(2018);
      await click(DatePeriodPage.submit());
      await expect(await $(DatePeriodPage.errorNumber(1)).getText()).toBe("Enter a date after 12 December 2016");
    });
  });

  describe("Given I enter a date after the maximum offset value date", () => {
    it("When I continue, Then I should see a period validation error", async () => {
      await $(DatePeriodPage.dateRangeFromDay()).setValue(13);
      await $(DatePeriodPage.dateRangeFromMonth()).setValue(7);
      await $(DatePeriodPage.dateRangeFromYear()).setValue(2017);
      await click(DatePeriodPage.submit());

      await $(DatePeriodPage.dateRangeToDay()).setValue(3);
      await $(DatePeriodPage.dateRangeToMonth()).setValue(3);
      await $(DatePeriodPage.dateRangeToYear()).setValue(2018);
      await click(DatePeriodPage.submit());
      await expect(await $(DatePeriodPage.errorNumber(1)).getText()).toBe("Enter a date before 2 July 2017");
    });
  });

  describe("Given I enter a date before the minimum offset answer id date", () => {
    it("When I continue, Then I should see a period validation error", async () => {
      await $(DatePeriodPage.dateRangeFromDay()).setValue(13);
      await $(DatePeriodPage.dateRangeFromMonth()).setValue(11);
      await $(DatePeriodPage.dateRangeFromYear()).setValue(2016);
      await click(DatePeriodPage.submit());

      await $(DatePeriodPage.dateRangeToDay()).setValue(13);
      await $(DatePeriodPage.dateRangeToMonth()).setValue(1);
      await $(DatePeriodPage.dateRangeToYear()).setValue(2018);
      await click(DatePeriodPage.submit());
      await expect(await $(DatePeriodPage.errorNumber(2)).getText()).toBe("Enter a date after 10 February 2018");
    });
  });

  describe("Given I enter a date in between the minimum offset meta date and the maximum offset value date", () => {
    it("When I continue, Then I should be able to reach the summary", async () => {
      await $(DatePeriodPage.dateRangeFromDay()).setValue(13);
      await $(DatePeriodPage.dateRangeFromMonth()).setValue(12);
      await $(DatePeriodPage.dateRangeFromYear()).setValue(2016);
      await click(DatePeriodPage.submit());

      await $(DatePeriodPage.dateRangeToDay()).setValue(11);
      await $(DatePeriodPage.dateRangeToMonth()).setValue(2);
      await $(DatePeriodPage.dateRangeToYear()).setValue(2018);
      await click(DatePeriodPage.submit());
      await verifyUrlContains(SubmitPage.pageName);
    });
  });

  async function completeFirstDatePage() {
    await $(DatePage.day()).setValue(1);
    await $(DatePage.month()).setValue(1);
    await $(DatePage.year()).setValue(2018);
    await click(DatePage.submit());
  }
});
