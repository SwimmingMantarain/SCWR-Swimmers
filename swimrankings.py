import requests
import time
from bs4 import BeautifulSoup

def get_swimmer_gender(sw_id: int):
    """
    Scrapes swimranings.net to find a swimmers gender base on the `sw_id`

    Side effects:
    - Scrapes swimrankings.net. Many calls to this function (from experience 31 requests in less than a second) in a short period of time can cause swimrankings.net to sh*t its pants and crash.
        The reason for this is because its server os is Windows. lmaoo

    Args:
        sw_id (int): Swimrankings unique key for the swimmer

    Returns:
        int: 0 if the swimmer is a man, 1 otherwise (a woman obviously).

    Raises:
        RuntimeError: If `response.status_code` isn't 200 and if `sw_id` isn't valid
    """
    url = f'https://www.swimrankings.net/index.php?page=athleteDetail&athleteId={sw_id}'
    response = requests.get(url)

    if response.status_code == 200 and response.text:
        try:
            # prevent swimrankings.net's Windows from sh*tting itself
            time.sleep(1.0)
            soup = BeautifulSoup(response.text, 'html.parser')
            header_div = soup.find('div', attrs={'id': 'header_athleteDetail'})
            img = header_div.find('img', attrs={'align': 'top'})
            # returning 0 for the men to not have the feminists yell at me
            if img['src'] == 'images/gender1.png':
                return 0
            else:
                return 1

        except:
            raise RuntimeError("[SCRSPING ERROR]: Failed to find swimmer's gender! Maybe id is wrong?")
    else:
        raise RuntimeError(f"[SCRAPING ERROR]: `Failed to scrape: {response.status_code}`")

def get_scwr_swimmers():
    """
    Get swimmers registered as part of the SCWR swimming club

    Side effects:
    - Scrapes swimrankings.net. Many calls to this function (from experience 31 requests in less than a second) in a short period of time can cause swimrankings.net to sh*t its pants and crash.
        The reason for this is because its server os is Windows. lmaoo

    Returns:
        list: a list of lists with the structure:
                [swimrankings unique id, birth year, first name, last name, gender]

    Raises:
        RuntimeError: If `response.status_code` isn't 200
    """
    url = 'https://www.swimrankings.net/index.php?page=rankingDetail&clubId=73626&gender=1&season=2025&course=LCM&agegroup=0&stroke=9'
    response = requests.get(url)

    if response.status_code == 200 and response.text:
        soup = BeautifulSoup(response.text, 'html.parser')
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

                gender = get_swimmer_gender(athlete_id)

                athletes.append([athlete_id, birth_year, first_name, last_name, gender])

        return athletes

    else:
        raise RuntimeError(f"[SCRAPING ERROR]: `Failed to scrape: {response.status_code}`")

def get_swimmer(full_name: str):
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
    url = f'https://www.swimrankings.net/index.php?&internalRequest=athleteFind&athlete_clubId=-1&athlete_gender=-1&athlete_lastname={last_name}&athlete_firstname={first_name}'
    response = requests.get(url)

    if response.status_code == 200 and response.text:
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
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

            gender = get_swimmer_gender(athlete_id)

            return [athlete_id, birth_year, first_name, last_name, gender]
        
        except:
            raise RuntimeError("[SCRSPING ERROR]: Failed to find swimmer's data! Maybe name is wrong?")

    else:
        raise RuntimeError(f"[SCRAPING ERROR]: `Failed to scrape: {response.status_code}`")
