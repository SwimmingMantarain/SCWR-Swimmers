from ..base_scraper import BaseScraper, ScraperError, ScraperUnimplementedError
from .swimrankings_types import *
from datetime import datetime

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

    async def get_belgium_meets(self) -> list[Meet]:
        url = self.url_book.belgium_meets()
        resp = await self._fetch(url, self.key)
        data = resp.json()["splashme"]

        meets = []

        for country in data:
            if country["code"] == "BEL":
                for meet in country["meets"]:
                    meets.append(Meet(
                        datetime.strptime(meet["startdate"], "%Y-%m-%d").date(),
                        datetime.strptime(meet["enddate"], "%Y-%m-%d").date(),
                        int(meet["liveid"]),
                        int(meet["id"]),
                        int(meet["course"]),
                        datetime.strptime(meet["lastupdate"], "%Y-%m-%dT%H:%M:%S"),
                        meet["name"],
                        meet["city"],
                    ))

        return meets

    async def get_club_athletes(self, clubid: int = 73626) -> list[Swimmer]:
        raise ScraperUnimplementedError()

    async def get_athlete(self, full_name: str) -> Swimmer:
        raise ScraperUnimplementedError()

    async def get_athlete_personal_bests(self, athlete_id: int) -> list[SwimmerPb]:
        raise ScraperUnimplementedError()

async def get_scraper(api_key: str = "") -> SwimrankingsApiScraper:
    scraper = SwimrankingsApiScraper(api_key)
    await scraper.__aenter__()
    return scraper
