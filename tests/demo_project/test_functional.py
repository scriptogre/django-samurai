from playwright.sync_api import Page, expect


def test_page_works(page: Page):
    page.goto("http://localhost:8000")
    expect(page).to_have_title("The install worked successfully! Congratulations!")
