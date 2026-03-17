# playwright-python-htmx-example.py
#
# Canonical example: Playwright e2e test for a Python/FastAPI HTMX backend
# using pytest-playwright.
#
# Setup (run once after cloning):
#
#   uv venv --python 3.12 .venv_tools
#   uv pip install --python .venv_tools/bin/python pytest pytest-playwright playwright
#   .venv_tools/bin/playwright install chromium
#
# Run:
#
#   .venv_tools/bin/pytest tests/e2e/
#
# Or with an explicit base URL:
#
#   .venv_tools/bin/pytest tests/e2e/ --base-url http://localhost:8000
#
# The backend must be running before the test suite executes. Start it with:
#
#   .venv_tools/bin/uvicorn src.app.main:app --reload
#
# The `page` fixture is provided automatically by pytest-playwright.
# Never use `python -m pytest` or bare `pytest` — always use .venv_tools/bin/pytest.

from playwright.sync_api import Page, expect


def test_htmx_filter_fragment(page: Page) -> None:
    """Verify that clicking a filter triggers an HTMX swap and the resulting
    fragment reflects the correct backend query result.

    Arrange → Act → Assert. Assertions are semantic (count, label text), not visual.
    This mirrors the TypeScript canonical examples in this directory.
    """
    # Arrange: navigate to the main listing page
    page.goto("http://localhost:8000/")

    # Act: activate a category filter
    page.locator("[data-filter='category'][data-value='electronics']").click()

    # Wait for the HTMX fragment swap to complete
    results_list = page.locator("#results-list")
    results_list.wait_for()

    # Assert: result items in the swapped fragment match the filter predicate
    items = page.locator("#results-list [data-item]")
    expect(items).to_have_count(12)

    # Assert: the result count label exposed by the backend matches the item count
    count_label = page.locator("[data-result-count]")
    expect(count_label).to_have_text("12")


def test_htmx_filter_clear(page: Page) -> None:
    """Verify that clearing an active filter restores the full result set
    and updates the count label to match.
    """
    # Arrange: navigate and apply a filter first
    page.goto("http://localhost:8000/")
    page.locator("[data-filter='category'][data-value='electronics']").click()
    page.locator("#results-list").wait_for()

    # Act: clear the filter
    page.locator("[data-clear-filters]").click()
    page.locator("#results-list").wait_for()

    # Assert: full result set is restored
    items = page.locator("#results-list [data-item]")
    expect(items).to_have_count(100)


def test_htmx_filter_count_label_updates(page: Page) -> None:
    """Verify that per-facet counts in the filter panel update when a filter
    is active — the count label narrows to match the filtered subset.
    """
    # Arrange
    page.goto("http://localhost:8000/")

    # Act: activate a filter
    page.locator("[data-filter='category'][data-value='electronics']").click()
    page.locator("#results-list").wait_for()

    # Assert: the facet count label for the active category reflects the filtered set
    facet_count = page.locator(
        "[data-facet='category'][data-value='electronics'] [data-facet-count]"
    )
    expect(facet_count).to_have_text("12")

    # Assert: a sibling facet's count is also scoped to the current filter state
    other_facet_count = page.locator(
        "[data-facet='category'][data-value='books'] [data-facet-count]"
    )
    expect(other_facet_count).to_have_text("0")
