from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
from time import sleep
import re


live_matches = 'https://1x001.com/it/live/football' # link pagina partite live
line_matches = 'https://1x001.com/it/line/football' # link pagina partite line

MATCHES_INFO = []

# aggiungere eventuali altri nomi di sezioni da non prendere in considerazione per il parsing
TO_SKIP = ['Speciali scommesse sul giorno della partita']


service = Service(r'/home/umberto/Scrivania/Sviluppo/Personale/1x001-Scraper/geckodriver')#r'./geckodriver')
driver = Firefox(service = service)


def get_URL_ID(match):
    match_info = match.find_element(By.XPATH, './div/a')
    url = match_info.get_attribute('href')
    parts = url.split('/')
    new_url = '/'.join(parts[:-1]) # Remove the last part
    id_match = re.findall("/[0-9]+-", new_url)
    print(id_match)
    id = id_match[0][1:-1]
    return new_url, id

def get_match_time(match):
    match_time_str = match.find_element(By.XPATH, './div/div/div[2]/span').text
    parts = match_time_str.split('/')
    # Extract the date and hour
    if len(parts) >= 5:
        date = f'{parts[0].strip()}/{parts[1].strip()}/{parts[2].strip()}'
        hour = parts[3].strip()
    else:
        date = ""
        hour = ""
    return date, hour

def get_championship_info(championship, championship_title):
    matches = WebDriverWait(championship, 30).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
    for match in matches:
        url, id = get_URL_ID(match)
        date, hour = get_match_time(match)
        data = (championship_title, url, id, date, hour)
        MATCHES_INFO.append(data)
        print(f'{data}') ##

# Controlla se per una nazione esistono sottocampionati (es. Italia/Serie A; Italia/Serie B)  
def check_if_matches(champ_element):
    attr = champ_element.get_attribute('class')
    return True if attr == 'ui-nav-item sports-menu-game' else False

def try_recursive(championships):
    for championship in championships:
        champ = WebDriverWait(championship, 30).until(EC.element_to_be_clickable((By.XPATH, './div')))
        champ_title = champ.get_attribute('title')
        if champ_title in TO_SKIP: continue
        print(champ_title) ##
        WebDriverWait(championship, 30).until(EC.element_to_be_clickable(champ))
        champ.location_once_scrolled_into_view
        champ.click()
        champ_elements = WebDriverWait(championship, 30).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
        found_matches = check_if_matches(champ_elements[0])
        print(found_matches)
        if found_matches:
            get_championship_info(championship, champ_title)
            champ.click()
        else:
            subchampionships = WebDriverWait(championship, 20).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
            print(f'Number of subchampionships n: {len(subchampionships)}')
            try_recursive(subchampionships)

def parse():
    sleep(5) ##
    sports_menu = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CLASS_NAME, 'sports-menu'))) # menù 'Sport'
    sports_menu_main = WebDriverWait(sports_menu, 50).until(EC.presence_of_element_located((By.CLASS_NAME, 'sports-menu-main-full__inner')))
    sports = WebDriverWait(sports_menu_main, 50).until(EC.presence_of_all_elements_located((By.XPATH, './div[1]/nav/ul/li')))
    sport = None
    for sport in sports:
        sel_sport = WebDriverWait(sport, 50).until(EC.presence_of_element_located((By.XPATH, './div')))
        sport_name = sel_sport.get_attribute('title')
        if sport_name == 'Calcio': break

    
    championships = WebDriverWait(sport, 50).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
    print(f'Number of championships n: {len(championships)}')
    try_recursive(championships[:15])
    '''
    championships = WebDriverWait(sport, 50).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
    print(f'Number of championships n: {len(championships)}')
    for championship in championships[:15]:
        champ = WebDriverWait(championship, 30).until(EC.element_to_be_clickable((By.XPATH, './div')))
        champ_title = champ.get_attribute('title')
        if champ_title in TO_SKIP: continue
        print(champ_title) ##
        WebDriverWait(championship, 30).until(EC.element_to_be_clickable(champ))
        champ.location_once_scrolled_into_view
        champ.click()
        champ_elements = WebDriverWait(championship, 30).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
        found_matches = check_if_matches(champ_elements[0])
        print(found_matches)
        if found_matches:
            get_championship_info(championship, champ_title)
            champ.click()
        else:
            subchampionships = WebDriverWait(championship, 20).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
            print(f'Number of subchampionships n: {len(subchampionships)}')
            for subchampionship in subchampionships:
                subchamp = WebDriverWait(subchampionship, 30).until(EC.element_to_be_clickable((By.XPATH, './div')))
                subchamp_title = subchamp.get_attribute('title')
                print(subchamp_title) ##
                WebDriverWait(subchampionship, 30).until(EC.element_to_be_clickable(subchamp))
                subchamp.location_once_scrolled_into_view
                subchamp.click()
                subchamp_elements = WebDriverWait(championship, 30).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
                found_matches = check_if_matches(subchamp_elements[0])
                print(found_matches)
                if found_matches:
                    get_championship_info(subchampionship, subchamp_title)
                    subchamp.click()
                #get_championship_info(subchampionship, subchamp_title)
                #subchamp.click()
    '''

    #print(MATCHES_INFO)

    # scrive file delle quote
    if live: ext = 'live'
    else: ext = 'line'
    with open(f'{ext}_links_{date_time}.csv', 'w') as matches_file: #, encoding="utf-8"
        if live:
            for info in MATCHES_INFO:
                matches_file.write(f'{info[0]},{info[1]},{info[2]},{info[3]},{info[4]}\n')
        else:
            for info in MATCHES_INFO:
                matches_file.write(f'{info[0]},{info[1]},{info[2]},{info[3]},{info[4]}\n')
        matches_file.close()

    print(f'\nFile {ext}_links_{date_time}.csv completato.\n') ##
    return


now = datetime.now()
date_time = now.strftime('%Y%m%d_%H%M')

#live = True  # live parsing
live = False # line parsing
driver.get(live_matches) if live else driver.get(line_matches)
driver.maximize_window()
parse()

driver.close()