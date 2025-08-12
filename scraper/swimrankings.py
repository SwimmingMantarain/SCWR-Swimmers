from enum import Enum
from dataclasses import dataclass
from typing import AsyncGenerator
from .base_scraper import BaseScraper, DataNotFoundError, HTMLParsingError

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


class UrlBook:
    def __init__(self):
        self.base = "https://www.swimrankings.net/index.php?"

    def swimmer_portfolio_page_by_id(self, sw_id: int) -> str:
        return f'{self.base}page=athleteDetail&athleteId={sw_id}'

    def swimmer_portfolio_page_by_full_name(self, first_name: str, last_name: str):
        return (
            f'{self.base}&internalRequest=athleteFind'
            f'&athlete_clubId=-1&athlete_gender=-1'
            f'&athlete_lastname={last_name}&athlete_firstname={first_name}'
        )

    def club_athletes(self, clubid: int):
        return (
                f'{self.base}page=rankingDetail&clubId={clubid}&gender=1'
                f'&season=2025&course=LCM&agegroup=0&stroke=9'
        )

class SwimrankingsScraper(BaseScraper):
    def __init__(self):
        super().__init__(UrlBook())

    def _parse_athlete_row(self, row, gender: Gender) -> Swimmer:
        td_name = row.find('td', attrs={'class': "name"})

        if td_name is None:
            raise HTMLParsingError("Failed to find required html! Tag `td`, `class`: `name`")

        a_name = td_name.find('a')

        if a_name is None:
            raise HTMLParsingError("Failed to find required html! Tag `a`")

        last_name, first_name = a_name.get_text().split(', ')
        last_name = last_name.title()

        a_href = a_name['href']
        try:
            athlete_id = int(a_href[30:37])
        except KeyError:
            raise DataNotFoundError(f"Failed to find athlete_id!, Maybe html changed: `{a_name}`")

        td_byear = row.find('td', attrs={'class': "date"})

        if td_byear is None:
            raise HTMLParsingError("Failed to find required html! Tag `td`, `class`: `date`")

        birth_year = int(td_byear.get_text())

        # safe to assume there is a 'td' at this point
        cols = row.find_all('td')

        try:
            td_gender = cols[3]
            img_gender = td_gender.find('img')

            if img_gender is not None:
                img_src = img_gender.get('src')

                if img_src == 'images/gender1.png':
                    gender = Gender(0)
                elif img_src == 'images/gender2.png':
                    gender = Gender(1)
                else:
                    raise HTMLParsingError(f"Unknown gender image was parsed: `{img_src}`")

        except IndexError:
            # TODO: Add logging here
            pass


        return Swimmer(
            athlete_id,
            birth_year,
            first_name,
            last_name,
            gender
        )

    async def _fetch_club_athletes(self, clubid: int) -> list[Swimmer]:
        """
        Get swimmers registered as part of the SCWR swimming club

        Side effects:
        - Scrapes swimrankings.net. Many calls to this function (from experience 31 httpx in less than a second) in a short period of time can cause swimrankings.net to sh*t its pants and crash.
            The reason for this is because its server os is Windows. lmaoo

        Returns:
            list[Swimmer]: A list of Swimmer objects containing swimmer data

        Raises:
            RuntimeError: If `response.status_code` isn't 200
        """
        url = self.url_book.club_athletes(clubid)
        response = await self._fetch(url)
        soup = self._parse(response.text)

        table1 = soup.find('table', attrs={'cellspacing': '0', 'cellpadding': '0', 'border': '0'})

        if table1 is None:
            raise HTMLParsingError("Failed to find required html! Tag: `table`, `cellspacing`: `0`")

        tables = table1.find_all('table', attrs={'class': 'athleteList'})

        if tables is None:
            raise HTMLParsingError("Failed to find required html! Tag: `table`, `class`: `athleteList`")

        boy_table = tables[0]

        if boy_table is None:
            raise HTMLParsingError("Failed to find required html! Tag `table`, `class`: `athleteList` (boy_table)")

        girl_table = tables[1]

        if girl_table is None:
            raise HTMLParsingError("Failed to find required html! Tag `table`, `class`: `athleteList` (girl_table)")

        athletes = []

        rows = boy_table.find_all('tr', attrs={'class': ["athleteSearch0", "athleteSearch1"]})

        if rows is None:
            raise HTMLParsingError("Failed to find required html! Tag `tr`, `class`: [`athleteSearch0`, `athleteSearch1`]")

        for row in rows:
            athlete = self._parse_athlete_row(row, Gender(0))
            athletes.append(athlete)

        rows = girl_table.find_all('tr', attrs={'class': ["athleteSearch0", "athleteSearch1"]})

        if rows is None:
            raise HTMLParsingError("Failed to find required html! Tag `tr`, `class`: [`athleteSearch0`, `athleteSearch1`]")

        for row in rows:
            athlete = self._parse_athlete_row(row, Gender(1))
            athletes.append(athlete)

        return athletes


    async def _fetch_athlete(self, full_name: str) -> Swimmer:
        """
        Scrapes swimrankings to find data about a swimmer based on a comma seperated name that is provided

        Side effects:
        - Scrapes swimrankings.net. Many calls to this function (from experience 31 requests in less than a second) in a short period of time can cause swimrankings.net to sh*t its pants and crash.
            The reason for this is because its server os is Windows. lmaoo

        Args:
            full_name (str): The full name of the swimmer seperated by a ', '

        Returns:
            Swimmer: A Swimmer object containing the swimmer's data

        Raises:
            RuntimeError: If `response.status_code` isn't 200 and if `sw_id` isn't valid
        """
        first_name, last_name = full_name.split(', ')
        url = self.url_book.swimmer_portfolio_page_by_full_name(first_name, last_name)
        response = await self._fetch(url)
        soup = self._parse(response.text)

        table = soup.find("table", attrs={'class': 'athleteSearch'})

        if table is None:
            raise HTMLParsingError("Failed to find required html! Tag `table`, `class`: `athleteSearch`")

        row = table.find('tr', attrs={'class': 'athleteSearch0'})

        if row is None:
            raise HTMLParsingError("Failed to find required html! Tag `tr`, `class`: `athleteSearch0`")
        
        athlete = self._parse_athlete_row(row, Gender(1))

        return athlete

    async def fetch_club_athletes(self, clubid: int = 73626) -> list[Swimmer]:
        return await self._fetch_club_athletes(clubid)

    async def fetch_athlete(self, full_name: str) -> Swimmer:
        return await self._fetch_athlete(full_name)

async def get_scraper() -> AsyncGenerator[SwimrankingsScraper, None]:
    async with SwimrankingsScraper() as scraper:
        yield scraper
