import re
from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # 1. Navigate to the page
        page.goto("http://localhost:5173/", timeout=60000)
        page.wait_for_timeout(10000) # Wait 10 seconds for rendering

        # Screenshot before action
        page.screenshot(path="jules-scratch/verification/debug_before_click.png")

        # 2. Select a date
        # Find the first enabled button within the calendar grid
        calendar_grid = page.locator(".rdp-months")
        first_available_day = calendar_grid.locator("button:not([disabled])").first
        first_available_day.click(timeout=60000)

        # 3. Select a time slot
        # Let's click the first available time slot
        page.locator(".time-slot-button").first.click()

        # 4. Fill in the form
        page.get_by_label("Ваше имя").fill("Jules Verne")
        page.get_by_label("Телефон").fill("+79991234567")

        # 5. Accept terms
        page.get_by_label("Я принимаю условия").check()
        page.get_by_label("Я согласен на обработку").check()
        # The third checkbox for studio rules was removed in a previous refactoring
        # so we don't need to check it.

        # 6. Submit the form
        page.get_by_role("button", name="Отправить заявку").click()

        # 7. Assert that the success toast appears
        success_toast = page.locator(".fixed.bottom-4.right-4")
        expect(success_toast).to_be_visible()
        expect(success_toast).to_have_text(re.compile("успешно отправлена"))

        # 8. Take a screenshot
        page.screenshot(path="jules-scratch/verification/verification.png")

    finally:
        context.close()
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
