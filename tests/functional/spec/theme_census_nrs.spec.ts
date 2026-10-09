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
      await expect(page.locator('.ons-header__org-logo--large img')).toHaveAttribute('src', /\/images\/nrs-logo\.svg$/)
      await expect(page.locator('.ons-header__org-logo--large img')).toHaveAttribute('alt', 'NRS - Home')
      await expect(page.locator('.ons-header__org-logo--large img')).toHaveAttribute('title', 'NRS - Home')
      await expect(page.locator('.ons-header__title-logo img')).toHaveAttribute('src', /\/images\/census-logo\.svg$/)
      await expect(page.locator('.ons-header__title-logo img')).toHaveAttribute('alt', 'Census Test 2027 - Home')
      await expect(page.locator('.ons-footer__logo-container img')).toHaveAttribute('src', /\/images\/nrs-footer-logo\.svg$/)
      await expect(page.locator('.ons-footer__logo-container img')).toHaveAttribute('alt', 'NRS - National Records of Scotland')
      await expect(page.locator('.ons-footer__logo-container img')).toHaveAttribute('title', 'NRS - National Records of Scotland')
    })
  })
})
