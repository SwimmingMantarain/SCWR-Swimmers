import requests
from bs4 import BeautifulSoup

def get_scwr_swimmers():
    url = 'https://www.swimrankings.net/index.php?page=rankingDetail&clubId=73626&gender=1&season=2025&course=LCM&agegroup=0&stroke=9'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', attrs={'class': 'athleteList'})
        # athlete: [swimrankings id, birth year, first name, last name]
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
                last_name = last_name.capitalize()

                birth_year = int(td_byear.get_text())

                athletes.append([athlete_id, birth_year, first_name, last_name])

        return athletes

    else:
        print(f"Failed to fetch SCWR athletes: {response.status_code}")

def get_swimmer(full_name: str):
    first_name, last_name = full_name.split(', ')
    url = f'https://www.swimrankings.net/index.php?&internalRequest=athleteFind&athlete_clubId=-1&athlete_gender=-1&athlete_lastname={last_name}&athlete_firstname={first_name}'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", attrs={'class': 'athleteSearch'})
        row = table.find('tr', attrs={'class': 'athleteSearch0'})

        td_name = row.find('td', attrs={'class': 'name'})
        td_date = row.find('td', attrs={'class': 'date'})

        birth_year = int(td_date.get_text())

        a_name = td_name.find('a')
        last_name, first_name = a_name.get_text().split(', ')
        last_name.capitalize()

        a_href = a_name['href']
        athlete_id = int(a_href[30:37])

        return [athlete_id, birth_year, first_name, last_name]

    else:
        print(f"Failed to fetch Athlete {full_name}: {response.status_code}")
