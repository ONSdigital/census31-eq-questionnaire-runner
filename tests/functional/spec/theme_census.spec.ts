import { test, expect } from '../fixtures/test'
import RadioPage from '../generated_pages/theme_census/radio.page'

test.describe('Theme Census', () => {
  test.describe('Given I launch a Census themed questionnaire', () => {
    test.beforeEach(async ({ openQuestionnaire }) => {
      await openQuestionnaire('test_theme_census.json', { theme: 'census' })
    })

    test('When I navigate to the radio page, Then I should see Census theme content', async ({ page }) => {
      const radioPage = new RadioPage(page)
      await expect(page).toHaveURL(new RegExp(radioPage.pageName))
      await expect(page.locator('#ons-logo-stacked-en-alt').first()).toContainText('Office for National Statistics')
      await expect(page.locator('#census-large-logo-en-alt').first()).toContainText('Census Test 2027')
      await expect(page.locator('#ons-logo-en-footer-alt').first()).toContainText('Office for National Statistics')
    })
  })
})
