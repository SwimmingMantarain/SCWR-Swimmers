from .swimrankings_api import get_scraper as get_api_scraper
from .swimrankings_web import get_scraper as get_web_scraper
from .swimrankings_types import *

class SwimrankingsScraper:
    def __init__(self, key: str = ""):
        self.key = key

    async def init(self):
        self._api_instance = await get_api_scraper(self.key)
        self._web_instance = await get_web_scraper()

    async def get_club_athletes(self, clubid: int = 73626) -> list[Swimmer]:
        athletes = []
        try:
            athletes = await self._api_instance.get_club_athletes(clubid)
        except:
            # TODO: add logging
            athletes = await self._web_instance.get_club_athletes(clubid)
        finally:
            return athletes
    
    async def get_athlete(self, full_name: str) -> Swimmer:
        athlete = None
        try:
            athlete = await self._api_instance.get_athlete(full_name)
        except:
            # TODO: add logging
            athlete = await self._web_instance.get_athlete(full_name)
        finally:
            return athlete

    async def get_athlete_pbs(self, athlete_id: int) -> list[SwimmerPb]:
        pbs = []
        try:
            athlete = await self._api_instance.get_athlete_pbs(athlete_id)
        except:
            # TODO: add logging
            athlete = await self._web_instance.get_athlete_pbs(athlete_id)
        finally:
            return pbs

    async def get_belgium_meets(self) -> list[Meet]:
        meets = []
        try:
            meets = await self._api_instance.get_belgium_meets()
        except:
            # TODO: add logging
            meets = await self._web_instance.get_belgium_meets()
        finally:
            return meets
