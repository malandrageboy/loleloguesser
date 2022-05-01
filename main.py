from unittest import main
import requests
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://br.op.gg/summoners/br/malandrageboy"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'

def get_player_info():
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
    profile_name = profile_div.find('span', class_='name').text

    elo = soup.find('div', class_="tier-rank").text

    lp = soup.find('span', class_="lp").text.replace("LP", '').replace(' ', '')
    win_lose = soup.find('span', class_="win-lose").text.replace("WinRate", "").split(' ')
    wins = win_lose[0].replace('V', '').replace('W', '')
    loses = win_lose[1].replace('D', '').replace('L', '')
    win_rate = win_lose[3]


    position_stats_div = soup.find('td', class_="position-stats")
    main_role_div = position_stats_div.find_all('li')[0]

    main_role = main_role_div.find('div', class_="name").text
    role_ratio = main_role_div.find('span', class_="role-ratio").text
    role_win_ratio = main_role_div.find('span', class_="win-ratio").text.replace("WinRate", "").replace(' ', '')

    most_champion_div = soup.find("td", class_='most-champion')
    main_champion_div = most_champion_div.find_all('li')[0]
    main_champion_name = main_champion_div.find('div', class_='name')
    main_champion_win_lose = main_champion_div.find('div', class_='win-lose')
    main_champion_name = main_champion_div.find('div', class_='name')


    print(profile_name, elo, lp, wins, loses, win_rate, main_role, role_ratio, role_win_ratio, sep=" *-* ")


if __name__ == "__main__":
    get_player_info()