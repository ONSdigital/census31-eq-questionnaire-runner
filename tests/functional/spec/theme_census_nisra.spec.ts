import { test, expect } from '../fixtures/test'
import RadioPage from '../generated_pages/theme_census_nisra/radio.page'

test.describe('Theme Census-NISRA', () => {
  test.describe('Given I launch a Census-NISRA themed questionnaire', () => {
    test.beforeEach(async ({ openQuestionnaire }) => {
      await openQuestionnaire('test_theme_census_nisra.json', { theme: 'census-nisra' })
    })

    test('When I navigate to the radio page, Then I should see Census-NISRA theme content', async ({ page }) => {
      const radioPage = new RadioPage(page)
      await expect(page).toHaveURL(new RegExp(radioPage.pageName))
      await expect(page.locator('#census-large-logo-en-alt').first()).toContainText('Census Test 2027')
      await expect(page.locator('#nisra-logo-large-alt').first()).toContainText('Northern Ireland Statistics and Research Agency')
      await expect(page.locator('#nisra-footer-logo-alt').first()).toContainText('Northern Ireland Statistics and Research Agency')
    })
  })
})
