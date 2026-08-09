from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import Browser, async_playwright
from playwright.async_api import Error as PlaywrightError
from pydantic import AnyHttpUrl

from app.core.constants import (
    ALLOWED_URL_SCHEMES,
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
        scraped_pages: list[ScrapedPage] = []

        while pending_urls and len(visited_urls) < self._max_pages:
            current_url = pending_urls.popleft()
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
                    title = (
                        soup.title.get_text(strip=True)
                        if soup.title is not None
                        else current_url
                    )

                    scraped_pages.append(
                        ScrapedPage(
                            source_url=current_url,
                            title=title,
                            content=content,
                        )
                    )

            for link in soup.select(HTML_LINK_SELECTOR):
                href = link.get("href")

                if not isinstance(href, str):
                    continue

                candidate_url = self._normalize_url(urljoin(current_url, href))

                if (
                    self._is_allowed_url(candidate_url)
                    and candidate_url not in discovered_urls
                ):
                    discovered_urls.add(candidate_url)
                    pending_urls.append(candidate_url)

        return scraped_pages

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
