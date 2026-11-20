from urllib.parse import urlparse

class PlaywrightBrowser:
    """Read-only browser adapter. No form submission, purchasing, messaging or downloads."""
    def __init__(self, allowed_domains: set[str], headless=True):
        self.allowed_domains = {d.lower() for d in allowed_domains}
        self.headless = headless
        self._playwright = self._browser = self._page = None

    def _check_url(self, url):
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("Only absolute HTTPS URLs are allowed")
        host = parsed.hostname.lower()
        if not any(host == d or host.endswith("." + d) for d in self.allowed_domains):
            raise PermissionError(f"Domain not allowlisted: {host}")

    async def start(self):
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError("Install browser extra and run playwright install chromium") from exc
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._page = await self._browser.new_page()

    async def read_page(self, url, max_chars=12000):
        if self._page is None:
            raise RuntimeError("Browser not started")
        if not 1 <= max_chars <= 50000:
            raise ValueError("max_chars must be 1..50000")
        self._check_url(url)
        await self._page.goto(url, wait_until="domcontentloaded", timeout=20000)
        return {"url": url, "title": await self._page.title(),
                "text": (await self._page.locator("body").inner_text())[:max_chars]}

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = self._playwright = self._page = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.close()
