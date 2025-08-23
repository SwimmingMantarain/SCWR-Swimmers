from enum import Enum
from dataclasses import dataclass
from typing import AsyncGenerator
from datetime import datetime, timezone, time, date
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

@dataclass
class SwimmerPb:
    sw_style_id: int
    sw_result_id: int
    sw_meet_id: int
    sw_default_fina: str 
    event: str
    course: int
    time: time
    pts: int
    date: date
    city: str
    meet_name: str
    last_scraped: datetime

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

    def _parse_time_str(self, time_str: str) -> time:
        time_formats = [
            "%H:%M:%S.%f",
            "%M:%S.%f",
            "%S.%f"
        ]

        for fmt in time_formats:
            try:
                dt = datetime.strptime(time_str, fmt)

                hour = dt.hour if "%H" in fmt else 0
                minute = dt.minute if "%M" in fmt else 0
                second = dt.second
                microsecond = dt.microsecond

                return time(hour, minute, second, microsecond)

            except ValueError:
                continue

        raise ValueError(f"Time string '{time_str}' is not in a recognized format")

    def _parse_pb_table(self, rows, fina_text) -> list[SwimmerPb]:
        pbs = []

        for row in rows:
            td_event = row.find('td', attrs={"class": "event"})

            if not td_event:
                raise HTMLParsingError("Failed to find required html! Tag: `td`, `class`: `event`")

            a_event = td_event.find('a')

            if not a_event:
                raise HTMLParsingError("Failed to find required html! Tag: `a`")

            event_str = a_event.get_text()

            event_href = a_event.get('href')
            style_id = int(event_href[46:])

            td_course = row.find('td', attrs={'class': 'course'})

            if not td_course:
                raise HTMLParsingError("Failed to find required html! Tag: `td`, `class`: `course`")

            course = int(td_course.get_text()[:2])

            td_time = row.find('td', attrs={"class": "time"})

            if not td_time:
                raise HTMLParsingError("Failed to find required html! Tag: `td`, `class`: `time`")

            a_time = td_time.find('a')

            if not a_time:
                raise HTMLParsingError("Failed to find required html! Tag: `a`")

            time_str = a_time.get_text()
            timetime = self._parse_time_str(time_str)

            result_id = int(a_time.get("href")[22:])

            td_points = row.find('td', attrs={"class": "code"})

            if not td_points:
                raise HTMLParsingError("Failed to find required html! Tag: `td`, `class`: `code`")

            points_text = td_points.get_text()
            if points_text != '-':
                points = int(points_text)
            else:
                points = 0

            td_date = row.find('td', attrs={"class": "date"})

            if not td_date:
                raise HTMLParsingError("Failed to find required html! Tag: `td`, `class`: `date`")

            date_str = td_date.get_text()
            datedate = datetime.strptime(date_str, "%d %b %Y").date()

            td_city = row.find('td', attrs={"class": "city"})

            if not td_city:
                raise HTMLParsingError("Failed to find required html! Tag: `td`, `class`: `city`")

            a_city = td_city.find('a')

            if not a_city:
                raise HTMLParsingError("Failed to find required html! Tag: `a`")

            city_str = a_city.get_text()

            city_href = a_city.get('href')
            meet_id = int(city_href[24:30])

            meet_name = a_city.get('title')

            pb = SwimmerPb(
                style_id,
                result_id,
                meet_id,
                fina_text,
                event_str,
                course,
                timetime,
                points,
                datedate,
                city_str,
                meet_name,
                datetime.now(timezone.utc)
            )

            pbs.append(pb)


        return pbs

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

    async def _fetch_athlete_pbs(self, athlete_id: int) -> list[SwimmerPb]:
        url = self.url_book.swimmer_portfolio_page_by_id(athlete_id)
        response = await self._fetch(url)
        soup = self._parse(response.text)

        select = soup.find("select", attrs={"name": "points"})

        if not select:
            raise HTMLParsingError("Failed to find required html! Tag `select`, `name`: `points`")

        default_option = select.find('option', attrs={"selected": ""})

        if not default_option:
            raise HTMLParsingError("Failed to find required html! Tag `option`, `selected`: ``")

        fina_text = default_option.get_text()

        pb_table = soup.find("table", attrs={"class": "athleteBest"})

        if not pb_table:
            raise HTMLParsingError("Failed to find required html! Tag `table`, `class`: `athleteBest`")

        pb_rows = pb_table.find_all("tr")

        if not pb_rows:
            raise HTMLParsingError("Failed to find required html! Tag `tr`")

        pb_rows.pop(0) # Remove the headers


        pbs = self._parse_pb_table(pb_rows, fina_text)

        return pbs

    async def fetch_club_athletes(self, clubid: int = 73626) -> list[Swimmer]:
        return await self._fetch_club_athletes(clubid)

    async def fetch_athlete(self, full_name: str) -> Swimmer:
        return await self._fetch_athlete(full_name)

    async def fetch_athlete_personal_bests(self, athlete_id: int) -> list[SwimmerPb]:
        return await self._fetch_athlete_pbs(athlete_id)

async def get_scraper() -> AsyncGenerator[SwimrankingsScraper, None]:
    async with SwimrankingsScraper() as scraper:
        yield scraper
