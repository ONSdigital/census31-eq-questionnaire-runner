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
      await expect(page.locator('.ons-header__org-logo img')).toHaveAttribute('src', /\/images\/nisra-logo\.svg$/)
      await expect(page.locator('.ons-header__org-logo img')).toHaveAttribute('alt', 'NISRA - Home')
      await expect(page.locator('.ons-header__org-logo img')).toHaveAttribute('title', 'NISRA - Home')
      await expect(page.locator('.ons-header__title-logo img')).toHaveAttribute('src', /\/images\/census-logo\.svg$/)
      await expect(page.locator('.ons-header__title-logo img')).toHaveAttribute('alt', 'Census Test 2027 - Home')
      await expect(page.locator('.ons-footer__logo-container img')).toHaveAttribute('src', /\/images\/nisra-footer-logo\.svg$/)
      await expect(page.locator('.ons-footer__logo-container img')).toHaveAttribute('alt', 'NISRA - Northern Ireland Statistics and Research Agency')
      await expect(page.locator('.ons-footer__logo-container img')).toHaveAttribute('title', 'NISRA - Northern Ireland Statistics and Research Agency')
    })
  })
})
