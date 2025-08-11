from dataclasses import dataclass
from typing import AsyncGenerator
from bs4 import BeautifulSoup
from enum import Enum
from functools import wraps
import asyncio
import httpx
import time

def rate_limited(min_interval):
    def decorator(func):
        last_time_called = 0.0
        lock = asyncio.Lock()

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_time_called
            async with lock:
                elapsed = time.time() - last_time_called
                wait = min_interval - elapsed
                if wait > 0:
                    await asyncio.sleep(wait)
                result = await func(*args, **kwargs)
                last_time_called = time.time()
                return result
        
        return wrapper
    
    return decorator

class URLBook:
    def SwimmerPortfolioPageById(self, sw_id: int):
        url = f'https://www.swimrankings.net/index.php?page=athleteDetail&athleteId={sw_id}'
        return url

    def SwimmerPortfolioPageByFullName(self, first_name: str, last_name: str):
        url = f'https://www.swimrankings.net/index.php?&internalRequest=athleteFind&athlete_clubId=-1&athlete_gender=-1&athlete_lastname={last_name}&athlete_firstname={first_name}'
        return url

    def SCWRPage(self):
        url = 'https://www.swimrankings.net/index.php?page=rankingDetail&clubId=73626&gender=1&season=2025&course=LCM&agegroup=0&stroke=9'
        return url

class Gender(Enum):
    MALE = 0
    FEMALE = 1

@dataclass
class Swimmer:
    sw_id: int
    birth_year: int
    first_name: str
    last_name: str
    gender: Gender

class SwimrankingsScraper:
    def __init__(self, rate_limit: int = 1):
        self.rate_limit = rate_limit
        self.url_book = URLBook()
        self.client = httpx.AsyncClient()

    @rate_limited(1)
    async def _fetch(self, url: str):
        return await self.client.get(url)

    async def get_swimmer_gender(self, sw_id: int):
        """
        Scrapes swimranings.net to find a swimmers gender base on the `sw_id`

        Side effects:
        - Scrapes swimrankings.net

        Args:
            sw_id (int): Swimrankings unique key for the swimmer

        Returns:
            Gender: 0 if the swimmer is a man, 1 otherwise (a woman obviously).

        Raises:
            RuntimeError: If `response.status_code` isn't 200 and if `sw_id` isn't valid
        """
        url = self.url_book.SwimmerPortfolioPageById(sw_id)
        response = await self._fetch(url)

        if response.status_code == 200 and response.text:
            try:
                soup = BeautifulSoup(response.text, 'lxml')

                header_div = soup.find('div', attrs={'id': 'header_athleteDetail'})
                if header_div is None:
                    raise RuntimeError("Header div not found!")

                img = header_div.find('img', attrs={'align': 'top'})
                if not img:
                    raise RuntimeError("Img in header div not found!")

                if img['src'] == 'images/gender1.png':
                    return Gender(0)
                else:
                    return Gender(1)

            except:
                raise RuntimeError("[SCRAPING ERROR]: Failed to find swimmer's gender! Maybe id is wrong?")
        else:
            raise RuntimeError(f"[SCRAPING ERROR]: `Failed to scrape: {response.status_code}`")

    async def get_scwr_swimmers(self) -> list[Swimmer]:
        """
        Get swimmers registered as part of the SCWR swimming club

        Side effects:
        - Scrapes swimrankings.net. Many calls to this function (from experience 31 httpx in less than a second) in a short period of time can cause swimrankings.net to sh*t its pants and crash.
            The reason for this is because its server os is Windows. lmaoo

        Returns:
            list: a list of lists with the structure:
                    [swimrankings unique id, birth year, first name, last name, gender]

        Raises:
            RuntimeError: If `response.status_code` isn't 200
        """
        url = self.url_book.SCWRPage()
        response = await self._fetch(url)

        if response.status_code == 200 and response.text:
            soup = BeautifulSoup(response.text, 'lxml')
            tables = soup.find_all('table', attrs={'class': 'athleteList'})
            athletes = []
            for table in tables:
                rows = table.find_all('tr', attrs={'class': ["athleteSearch0", "athleteSearch1"]})
                for row in rows:
                    td_name = row.find('td', attrs={'class': "name"})
                    td_byear = row.find('td', attrs={'class': "date"})
                    a_name = td_name.find('a')

                    a_href = a_name['href']
                    athlete_id = int(a_href[30:37])
                    
                    last_name, first_name = a_name.get_text().split(', ')
                    last_name = last_name.title()

                    birth_year = int(td_byear.get_text())

                    gender = await self.get_swimmer_gender(athlete_id)

                    swimmer = Swimmer(
                        athlete_id,
                        birth_year,
                        first_name,
                        last_name,
                        gender
                    )

                    athletes.append(swimmer)

            return athletes

        else:
            raise RuntimeError(f"[SCRAPING ERROR]: `Failed to scrape: {response.status_code}`")

    async def get_swimmer(self, full_name: str):
        """
        Scrapes swimrankings to find data about a swimmer based on a comma seperated name that is provided

        Side effects:
        - Scrapes swimrankings.net. Many calls to this function (from experience 31 requests in less than a second) in a short period of time can cause swimrankings.net to sh*t its pants and crash.
            The reason for this is because its server os is Windows. lmaoo

        Args:
            full_name (str): The full name of the swimmer seperated by a ', '

        Returns:
            list: The data of the swimmer -> [swimrankings unique id, birth year, first name, last name, gender]

        Raises:
            RuntimeError: If `response.status_code` isn't 200 and if `sw_id` isn't valid
        """
        first_name, last_name = full_name.split(', ')
        url = self.url_book.SwimmerPortfolioPageByFullName(first_name, last_name)
        response = await self._fetch(url)

        if response.status_code == 200 and response.text:
            try:
                soup = BeautifulSoup(response.text, 'lxml')
                table = soup.find("table", attrs={'class': 'athleteSearch'})
                row = table.find('tr', attrs={'class': 'athleteSearch0'})

                td_name = row.find('td', attrs={'class': 'name'})
                td_date = row.find('td', attrs={'class': 'date'})

                birth_year = int(td_date.get_text())

                a_name = td_name.find('a')
                last_name, first_name = a_name.get_text().split(', ')
                last_name.title()

                a_href = a_name['href']
                athlete_id = int(a_href[30:37])

                gender = self.get_swimmer_gender(athlete_id)

                return [athlete_id, birth_year, first_name, last_name, gender]
            
            except:
                raise RuntimeError("[SCRAPING ERROR]: Failed to find swimmer's data! Maybe name is wrong?")

        else:
            raise RuntimeError(f"[SCRAPING ERROR]: `Failed to scrape: {response.status_code}`")

async def get_scraper() -> AsyncGenerator[SwimrankingsScraper, None]:
    scraper = SwimrankingsScraper()
    try:
        yield scraper
    finally:
        await scraper.client.aclose()
