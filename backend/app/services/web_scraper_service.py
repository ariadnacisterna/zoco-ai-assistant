from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import Browser, Page, async_playwright
from playwright.async_api import Error as PlaywrightError
from pydantic import AnyHttpUrl

from app.core.constants import (
    ALLOWED_URL_SCHEMES,
    HTML_EXPANDABLE_CONTAINER_SELECTOR,
    HTML_EXPANDABLE_CONTROL_SELECTOR,
    HTML_IGNORED_SELECTOR,
    HTML_LINK_SELECTOR,
    HTML_MAIN_SELECTOR,
    HTML_PARSER,
    HTML_TEXT_SEPARATOR,
    SCRAPER_WAIT_UNTIL,
)
from app.core.exceptions import KnowledgeSourceUnavailableError
from app.schemas.knowledge import ScrapedPage


class WebScraperService:
    """Extract public content from the configured ZOCO website."""

    def __init__(
        self,
        base_url: AnyHttpUrl,
        max_pages: int,
        timeout_ms: int,
    ) -> None:
        self._base_url = str(base_url).rstrip("/")
        self._max_pages = max_pages
        self._timeout_ms = timeout_ms
        self._allowed_domain = urlparse(self._base_url).netloc

    async def scrape(self) -> list[ScrapedPage]:
        """Crawl and extract public pages from the configured website."""

        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)

                try:
                    scraped_pages = await self._crawl(browser)
                finally:
                    await browser.close()
        except PlaywrightError as error:
            raise KnowledgeSourceUnavailableError from error

        if not scraped_pages:
            raise KnowledgeSourceUnavailableError

        return scraped_pages

    async def _crawl(
        self,
        browser: Browser,
    ) -> list[ScrapedPage]:
        pending_urls = deque([self._base_url])
        discovered_urls = {self._base_url}
        visited_urls: set[str] = set()
        processed_urls: set[str] = set()
        seen_content_keys: set[str] = set()
        scraped_pages: list[ScrapedPage] = []

        while pending_urls and len(processed_urls) < self._max_pages:
            current_url = pending_urls.popleft()

            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)

            page = await browser.new_page()

            try:
                response = await page.goto(
                    current_url,
                    wait_until=SCRAPER_WAIT_UNTIL,
                    timeout=self._timeout_ms,
                )

                if response is None or not response.ok:
                    continue

                resolved_url = self._normalize_url(page.url)

                if (
                    not self._is_allowed_url(resolved_url)
                    or resolved_url in processed_urls
                ):
                    continue

                processed_urls.add(resolved_url)
                discovered_urls.add(resolved_url)
                expanded_content = await self._collect_expandable_content(page)
                rendered_html = await page.content()
            except PlaywrightError:
                continue
            finally:
                await page.close()

            soup = BeautifulSoup(rendered_html, HTML_PARSER)

            for ignored_element in soup.select(HTML_IGNORED_SELECTOR):
                ignored_element.decompose()

            content_element = soup.select_one(HTML_MAIN_SELECTOR) or soup.body

            if content_element is not None:
                content = HTML_TEXT_SEPARATOR.join(
                    content_element.get_text(
                        HTML_TEXT_SEPARATOR,
                        strip=True,
                    ).split()
                )

                if content:
                    content = HTML_TEXT_SEPARATOR.join(
                        (content, *expanded_content),
                    )
                    content_key = self._content_key(content)

                    if content_key not in seen_content_keys:
                        seen_content_keys.add(content_key)
                        title = (
                            soup.title.get_text(strip=True)
                            if soup.title is not None
                            else resolved_url
                        )

                        scraped_pages.append(
                            ScrapedPage(
                                source_url=resolved_url,
                                title=title,
                                content=content,
                            )
                        )

            for link in soup.select(HTML_LINK_SELECTOR):
                href = link.get("href")

                if not isinstance(href, str):
                    continue

                candidate_url = self._normalize_url(urljoin(resolved_url, href))

                if (
                    self._is_allowed_url(candidate_url)
                    and candidate_url not in discovered_urls
                ):
                    discovered_urls.add(candidate_url)
                    pending_urls.append(candidate_url)

        return scraped_pages

    async def _collect_expandable_content(self, page: Page) -> list[str]:
        controls = page.locator(HTML_EXPANDABLE_CONTROL_SELECTOR)
        expanded_content: list[str] = []

        for control_index in range(await controls.count()):
            control = controls.nth(control_index)

            try:
                was_expanded = await control.get_attribute("aria-expanded") == "true"

                if not was_expanded:
                    await control.click()

                container = control.locator(HTML_EXPANDABLE_CONTAINER_SELECTOR)
                content = HTML_TEXT_SEPARATOR.join(
                    (await container.inner_text()).split()
                )

                if content:
                    expanded_content.append(content)

                if not was_expanded:
                    await control.click()
            except PlaywrightError:
                continue

        return expanded_content

    @staticmethod
    def _content_key(content: str) -> str:
        return "".join(
            character for character in content.casefold() if character.isalnum()
        )

    @staticmethod
    def _normalize_url(url: str) -> str:
        url_without_fragment = urldefrag(url)[0]
        parsed_url = urlparse(url_without_fragment)
        url_without_query = parsed_url._replace(query="")

        return url_without_query.geturl().rstrip("/")

    def _is_allowed_url(self, url: str) -> bool:
        parsed_url = urlparse(url)

        return (
            parsed_url.scheme in ALLOWED_URL_SCHEMES
            and parsed_url.netloc == self._allowed_domain
        )
