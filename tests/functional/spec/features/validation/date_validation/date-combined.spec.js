import DateRangePage from "../../../../generated_pages/date_validation_combined/date-range-block.page";
import SubmitPage from "../../../../generated_pages/date_validation_combined/submit.page";
import { click } from "../../../../helpers";

describe("Feature: Combined question level and single validation for dates", () => {
  before(async () => {
    await browser.openQuestionnaire("test_date_validation_combined.json");
  });

  describe("Period Validation", () => {
    describe("Given I enter dates", () => {
      it("When I enter a single dates that are too early/late, Then I should see a single validation errors", async () => {
        await $(DateRangePage.dateRangeFromDay()).setValue(12);
        await $(DateRangePage.dateRangeFromMonth()).setValue(12);
        await $(DateRangePage.dateRangeFromYear()).setValue(2016);

        await $(DateRangePage.dateRangeToDay()).setValue(22);
        await $(DateRangePage.dateRangeToMonth()).setValue(2);
        await $(DateRangePage.dateRangeToYear()).setValue(2017);
        await click(DateRangePage.submit());
        await expect(await $(DateRangePage.errorNumber(1)).getText()).toBe("Enter a date after 12 December 2016");
        await expect(await $(DateRangePage.errorNumber(2)).getText()).toBe("Enter a date before 22 February 2017");
      });

      it("When I enter a range too large, Then I should see a range validation error", async () => {
        await $(DateRangePage.dateRangeFromDay()).setValue(13);
        await $(DateRangePage.dateRangeFromMonth()).setValue(12);
        await $(DateRangePage.dateRangeFromYear()).setValue(2016);

        await $(DateRangePage.dateRangeToDay()).setValue(21);
        await $(DateRangePage.dateRangeToMonth()).setValue(2);
        await $(DateRangePage.dateRangeToYear()).setValue(2017);
        await click(DateRangePage.submit());
        await expect(await $(DateRangePage.errorNumber(1)).getText()).toBe("Enter a reporting period less than or equal to 50 days");
      });

      it("When I enter a range too small, Then I should see a range validation error", async () => {
        await $(DateRangePage.dateRangeFromDay()).setValue(1);
        await $(DateRangePage.dateRangeFromMonth()).setValue(1);
        await $(DateRangePage.dateRangeFromYear()).setValue(2017);

        await $(DateRangePage.dateRangeToDay()).setValue(10);
        await $(DateRangePage.dateRangeToMonth()).setValue(1);
        await $(DateRangePage.dateRangeToYear()).setValue(2017);
        await click(DateRangePage.submit());
        await expect(await $(DateRangePage.errorNumber(1)).getText()).toBe("Enter a reporting period greater than or equal to 10 days");
      });

      it("When I enter valid dates, Then I should see the summary page", async () => {
        await $(DateRangePage.dateRangeFromDay()).setValue(1);
        await $(DateRangePage.dateRangeFromMonth()).setValue(1);
        await $(DateRangePage.dateRangeFromYear()).setValue(2017);

        // Min range
        await $(DateRangePage.dateRangeToDay()).setValue(11);
        await $(DateRangePage.dateRangeToMonth()).setValue(1);
        await $(DateRangePage.dateRangeToYear()).setValue(2017);
        await click(DateRangePage.submit());
        await expect(await $(SubmitPage.dateRangeFrom()).getText()).toBe("1 January 2017 to 11 January 2017");

        // Max range
        await $(SubmitPage.dateRangeFromEdit()).click();
        await $(DateRangePage.dateRangeToDay()).setValue(20);
        await $(DateRangePage.dateRangeToMonth()).setValue(2);
        await $(DateRangePage.dateRangeToYear()).setValue(2017);
        await click(DateRangePage.submit());
        await expect(await $(SubmitPage.dateRangeFrom()).getText()).toBe("1 January 2017 to 20 February 2017");
      });
    });
  });
});
