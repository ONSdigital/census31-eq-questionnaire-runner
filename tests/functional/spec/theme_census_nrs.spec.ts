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
      await expect(page.locator('#census-large-logo-en-alt').first()).toContainText('Census Test 2027')
      await expect(page.locator('#nrs-logo-en-alt').first()).toContainText("Scotland's Census")
      await expect(page.locator('#nrs-footer-logo-en-alt').first()).toContainText("Scotland's Census")
    })
  })
})
