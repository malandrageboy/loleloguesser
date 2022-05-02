import requests
import bs4
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from db import Database, Summoner

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'

def get_player_info(URL: str):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={USER_AGENT}')
    driver = webdriver.Chrome(chrome_options=options, executable_path=ChromeDriverManager().install())
    # driver = webdriver.Chrome(chrome_options=options, executable_path="./chromedriver")

    driver.get(URL)
    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    profile_div = soup.find('div', class_="profile")
    profile_name = profile_div.find('span', class_='name').text.replace('[', '').replace(']', '')
    region = URL.split('/')[-2]

    elo = soup.find('div', class_="tier-rank").text.lower()
    lp = soup.find('span', class_="lp").text.replace("LP", '').replace(' ', '').lower()
    win_lose = soup.find('span', class_="win-lose").text.replace("WinRate", "").split(' ')
    wins = win_lose[0].replace('V', '').replace('W', '').lower()
    loses = win_lose[1].replace('D', '').replace('L', '').lower()
    win_rate = win_lose[3].lower().replace('%', '')

    position_stats_div = soup.find('td', class_="position-stats")
    main_role_div = position_stats_div.find_all('li')[0]

    main_role = main_role_div.find('div', class_="name").text.lower()
    role_ratio = main_role_div.find('span', class_="role-ratio").text.lower().lower().replace('%', '')
    role_win_ratio = main_role_div.find('span', class_="win-ratio").text.replace("WinRate", "").replace(' ', '').replace('%', '')

    most_champion_div = soup.find("td", class_='most-champion')
    main_champion_div = most_champion_div.find_all('li')[0]
    main_champion_name = main_champion_div.find('div', class_='name').text.lower()
    main_champion_win_lose = main_champion_div.find('div', class_='win-lose').text.replace('(', '').replace(")", '')

    main_champion_wins = main_champion_win_lose.split(' ')[1].replace('V', '').replace('W', '').lower()
    main_champion_loses = main_champion_win_lose.split(' ')[2].replace('D', '').replace('L', '').lower()
    main_champion_winrate = main_champion_div.find('b', class_="e1je0q1a0").text.lower().replace('%', '')

    main_champion_kda = main_champion_div.find('div', class_='e1je0q1a1').text.replace('KDA', '').replace(' ', '').lower()


    return Summoner(profile_name, region, elo, lp, wins, loses,
        win_rate, main_role, role_ratio, role_win_ratio,
        main_champion_name, main_champion_wins, main_champion_loses, main_champion_winrate,
        main_champion_kda)
    
def extract_player_names(CURRENT_PLAYING: str):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={USER_AGENT}')
    driver = webdriver.Chrome(chrome_options=options, executable_path=ChromeDriverManager().install())
    # driver = webdriver.Chrome(chrome_options=options, executable_path="./chromedriver")

    driver.get(CURRENT_PLAYING)
    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    currentGamesGrid = soup.find('ul', class_='currentGamesGrid')
    lis = currentGamesGrid.find_all('li')

    region = CURRENT_PLAYING.split('/')[-1]
    user_list = []

    for li in lis:
        users_divs = li.find_all('div', class_="name")
        users = []

        for user_div in users_divs: 
            user_name = user_div.text
            user_name = user_name.strip()
            users.append(user_name)

        for user in users: 
            user_list.append((user, region))
    
    with open('urls_players.txt', 'a') as file:
        text = ''
        for user in user_list:
            text += "https://br.op.gg/summoners/%s/%s" % (user[1], user[0]) + "\n"
        print(text)
        file.write(text)


PATH_DB = 'database.sqlite'

if __name__ == "__main__":
    db = Database(PATH_DB)
    db.create_table()
    db.close()

    # extract_player_names('https://porofessor.gg/current-games/br')
    urls_players = ''
    with open('urls_players.txt', 'r') as file:
        urls_players = file.read()

    for url in urls_players.split('\n'):
        if url == '': continue

        with open('urls_players.txt', 'w') as file:
            urls_players = urls_players.replace(url, '')
            file.write(urls_players)

        db = Database(PATH_DB)
        if db.exists(url.split('/')[-1]): 
            n = url.split('/')[-1]
            print(f'>> {n} existe. Pulando..')
            sleep(1)
            continue
        
        try:
            sum = get_player_info(url)
            print(sum)
            print('-=-')
            
            db.save_player(sum)
            db.close()
        except:
            print(f"Erro: url->{url}")
            