from .base_scraper import BaseScraper, ScraperError

class UrlBook:
    def __init__(self):
        self.base = "https://www.swimrankings.net/json/splashme"

    def belgium_meets(self) -> str:
        return f'{self.base}/meets?language=en&nations=BEL'

class SwimrankingsApiScraper(BaseScraper):
    def __init__(self, api_key: str):
        if not api_key: ScraperError("Api key needed to use API scraper!!!")
        self.key = api_key
        super().__init__(UrlBook())

    async def get_belgium_meets(self):
        url = self.url_book.belgium_meets()
        resp = await self._fetch(url, self.key)

        print(resp.json())

async def get_scraper(api_key: str = "") -> SwimrankingsApiScraper:
    scraper = SwimrankingsApiScraper(api_key)
    await scraper.__aenter__()
    return scraper
