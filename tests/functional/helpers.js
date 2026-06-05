export const checkItemsInList = async (itemsExpected, listLabel) => {
  await $(listLabel(1)).waitForDisplayed();

  for (let i = 1; i <= itemsExpected.length; i++) {
    await expect(await $(listLabel(i)).getText()).toContain(itemsExpected[i - 1]);
  }
};

export const summaryItemComplete = async (summaryItemLabel, status) => {
  await expect(await $(summaryItemLabel).$(`.ons-summary__item-title-icon.ons-summary__item-title-icon--check`).isExisting()).toBe(status);
};

export const listItemComplete = async (listItemLabel, status) => {
  await expect(await $(listItemLabel).$(`.ons-list__prefix.ons-list__prefix--icon-check`).isExisting()).toBe(status);
};

const assertSummaryFunction = (selector) => {
  return async (entities) => {
    // check each summary value/item/title is present and that the number of them matches what is on the page
    await entities.map(async (entity, index) => {
      await expect(await $$(selector)[index].getText()).toEqual(entity);
    });
    await expect(await $$(selector).length).toEqual(entities.length);
  };
};

export const assertSummaryValues = assertSummaryFunction(".ons-summary__values");
export const assertSummaryTitles = assertSummaryFunction(".ons-summary__title");
export const assertSummaryItems = assertSummaryFunction(".ons-summary__item--text");

export const repeatingAnswerChangeLink = (answerIndex) => {
  return $$('dd[class="ons-summary__actions"]')[answerIndex].$("a");
};

export const listItemIds = () => {
  return $$("[data-list-item-id]").map((listItem) => listItem.getAttribute("data-list-item-id"));
};

export const click = async (selector) => {
  // This was introduced due to a css property on ons-btn:
  // .ons-btn:active {
  //      top: 0.1666666667em
  //  }
  // When the button is right on the very edge of the screen, webdriverio sees that the button is accessible, so does not scroll
  // but clicks down on the very top of the button which moves down and just below the mouse. When the mouse click is released
  // it's no longer over the button and the click silently fails. This means that when the test comes to do assertions on the following page
  // they fail, as we never navigated to that page.
  await $(selector).scrollIntoView({ block: "center", inline: "center", behavior: "smooth" });
  await $(selector).click();

  // Allow time in case the click loads a new page.
  await browser.pause(100);
};

export const clickSyncMode = (selector) => {
  $(selector).scrollIntoView({ block: "end", inline: "center", behavior: "smooth" });
  $(selector).click();

  // Allow time in case the click loads a new page.
  browser.pause(100);
};

export const verifyUrlContains = async (expectedUrlString) => {
  await expect(browser).toHaveUrl(expect.stringContaining(expectedUrlString));
};

export const verifyUrlContainsSyncMode = (expectedUrlString) => {
  expect(browser).toHaveUrl(expect.stringContaining(expectedUrlString));
};

/**
 * Normalize HTML by removing extra whitespace and normalizing self-closing tags.
 * This helps tests be resilient to formatting changes in templates (e.g., pretty-printed vs minified HTML).
 * Converts: `<br />` to `<br>` and removes extra whitespace/newlines between tags.
 */
export const normalizeHtml = (html) => {
  return html
    .replace(/\s+/g, " ") // Replace multiple whitespace (including newlines) with single space
    .replace(/>\s+</g, "><") // Remove whitespace between tags
    .replace(/\s*(<br\s*\/?>)\s*/gi, "$1") // Remove whitespace around line-break tags
    .replace(/>\s+/g, ">") // Remove whitespace immediately after opening tags
    .replace(/\s+</g, "<") // Remove whitespace immediately before closing/opening tags
    .replace(/<br\s*\/>/g, "<br>") // Normalize XHTML br tags to HTML5
    .replace(/[\u2018\u2019]/g, "'") // Normalize smart apostrophes to ASCII apostrophe
    .trim();
};
