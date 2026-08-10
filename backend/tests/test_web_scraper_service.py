import asyncio
from unittest.mock import AsyncMock, Mock

from playwright.async_api import Browser, Page

from app.core.constants import (
    HTML_EXPANDABLE_CONTAINER_SELECTOR,
    HTML_EXPANDABLE_CONTROL_SELECTOR,
)
from app.services.web_scraper_service import WebScraperService

TEST_BASE_URL = "https://zocopagos.com"
TEST_RESOLVED_URL = "https://zocopagos.com/pagos"
TEST_PAGE_TITLE = "Pagos - ZOCO"
TEST_VISIBLE_CONTENT = "Preguntas frecuentes"
TEST_EXPANDED_CONTENT = (
    "¿Qué es un POS y para qué sirve? "
    "Un POS es una terminal que permite procesar cobros."
)


def test_crawl_collects_accordion_content_and_uses_redirect_target() -> None:
    response = Mock()
    response.ok = True

    container = Mock()
    container.inner_text = AsyncMock(return_value=TEST_EXPANDED_CONTENT)

    control = Mock()
    control.get_attribute = AsyncMock(return_value="false")
    control.click = AsyncMock()
    control.locator.return_value = container

    controls = Mock()
    controls.count = AsyncMock(return_value=1)
    controls.nth.return_value = control

    page = Mock(spec=Page)
    page.url = TEST_RESOLVED_URL
    page.goto = AsyncMock(return_value=response)
    page.content = AsyncMock(
        return_value=(
            f"<html><head><title>{TEST_PAGE_TITLE}</title></head>"
            f"<body><main>{TEST_VISIBLE_CONTENT}</main>"
            '<a href="/pagos">Inicio</a></body></html>'
        )
    )
    page.close = AsyncMock()
    page.locator.return_value = controls

    browser = Mock(spec=Browser)
    browser.new_page = AsyncMock(return_value=page)

    service = WebScraperService(
        base_url=TEST_BASE_URL,
        max_pages=10,
        timeout_ms=1_000,
    )

    pages = asyncio.run(service._crawl(browser))

    assert len(pages) == 1
    assert str(pages[0].source_url).rstrip("/") == TEST_RESOLVED_URL
    assert pages[0].title == TEST_PAGE_TITLE
    assert TEST_VISIBLE_CONTENT in pages[0].content
    assert TEST_EXPANDED_CONTENT in pages[0].content
    assert browser.new_page.await_count == 1
    assert control.click.await_count == 2
    page.locator.assert_called_once_with(HTML_EXPANDABLE_CONTROL_SELECTOR)
    control.locator.assert_called_once_with(HTML_EXPANDABLE_CONTAINER_SELECTOR)


def test_crawl_skips_pages_with_duplicate_content() -> None:
    response = Mock()
    response.ok = True

    controls = Mock()
    controls.count = AsyncMock(return_value=0)

    html = (
        f"<html><head><title>{TEST_PAGE_TITLE}</title></head>"
        f"<body><main>{TEST_VISIBLE_CONTENT}</main>"
        '<a href="/pagos">Inicio</a></body></html>'
    )

    root_page = Mock(spec=Page)
    root_page.url = f"{TEST_BASE_URL}/"
    root_page.goto = AsyncMock(return_value=response)
    root_page.content = AsyncMock(return_value=html)
    root_page.close = AsyncMock()
    root_page.locator.return_value = controls

    payments_page = Mock(spec=Page)
    payments_page.url = TEST_RESOLVED_URL
    payments_page.goto = AsyncMock(return_value=response)
    payments_page.content = AsyncMock(return_value=html)
    payments_page.close = AsyncMock()
    payments_page.locator.return_value = controls

    browser = Mock(spec=Browser)
    browser.new_page = AsyncMock(side_effect=[root_page, payments_page])

    service = WebScraperService(
        base_url=TEST_BASE_URL,
        max_pages=10,
        timeout_ms=1_000,
    )

    pages = asyncio.run(service._crawl(browser))

    assert len(pages) == 1
    assert str(pages[0].source_url).rstrip("/") == TEST_BASE_URL
    assert browser.new_page.await_count == 2


def test_collect_expandable_content_keeps_initially_open_control_open() -> None:
    container = Mock()
    container.inner_text = AsyncMock(return_value=TEST_EXPANDED_CONTENT)

    control = Mock()
    control.get_attribute = AsyncMock(return_value="true")
    control.click = AsyncMock()
    control.locator.return_value = container

    controls = Mock()
    controls.count = AsyncMock(return_value=1)
    controls.nth.return_value = control

    page = Mock(spec=Page)
    page.locator.return_value = controls

    service = WebScraperService(
        base_url=TEST_BASE_URL,
        max_pages=10,
        timeout_ms=1_000,
    )

    content = asyncio.run(service._collect_expandable_content(page))

    assert content == [TEST_EXPANDED_CONTENT]
    control.click.assert_not_awaited()
