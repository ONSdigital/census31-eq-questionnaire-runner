import { test, expect } from '../fixtures/test'
import RadioPage from '../generated_pages/theme_census_nrs/radio.page'

test.describe('Theme Census-NRS', () => {
  test.describe('Given I launch a Census-NRS themed questionnaire', () => {
    test.beforeEach(async ({ openQuestionnaire }) => {
      await openQuestionnaire('test_theme_census_nrs.json', { theme: 'census-nrs' })
    })

    test('When I navigate to the radio page, Then I should see Census-NRS theme content', async ({ page }) => {
      const radioPage = new RadioPage(page)
      await expect(page).toHaveURL(new RegExp(radioPage.pageName))
      await expect(page.locator('#ons-logo-stacked-en-alt').first()).toContainText('Office for National Statistics')
      await expect(page.locator('#census-logo-en-alt').first()).toContainText('Census 2021 logo')
      await expect(page.locator('#nrs-census-logo-en-alt').first()).toContainText('Census Scotland logo')
      await expect(page.locator('#nrs-census-footer-logo-en-alt').first()).toContainText('Census Scotland logo')
    })
  })
})
