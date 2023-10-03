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

QUOTATIONS_LIVE = ['ID,Championship,Team1,Team2,Date,Current_Time,1,X,2,Link']
QUOTATIONS_LINE = ['ID,Championship,Team1,Team2,Date,Hour,1,X,2,Link']

# aggiungere eventuali altri nomi di sezioni da non prendere in considerazione per il parsing
TO_SKIP = ['Speciali scommesse sul giorno della partita',
        'FIFA World Cup 2022. Vincitore',
        'FIFA World Cup 2022. Duel of the players',
        'FIFA World Cup 2022. Statistics of the group stage',
        'FIFA World Cup 2022. Scommesse speciali',
        'FIFA World Cup 2022. Matches of the Day']


service = Service(r'./geckodriver')
driver = Firefox(service = service)

# applicazione filtro 12h
def apply_filter():
    filter = '/html/body/div[1]/div/div/div[3]/div/div/div[2]/main/div[2]/div/div/div[1]/div[2]/div/div[2]/ul/li/div/div/button'
    WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.XPATH, filter))).click()

    time = '/html/body/div[1]/div/div/div[3]/div/div/div[2]/main/div[2]/div/div/div[1]/div[2]/div/div[2]/ul/li/div/div[2]/form/div[1]/div[1]/fieldset/div/div/div[1]/div/div'
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, time))).click()

    # < 12h
    hour = '/html/body/div[1]/div/div/div[3]/div/div/div[2]/main/div[2]/div/div/div[1]/div[2]/div/div[2]/ul/li/div/div[2]/form/div[1]/div[1]/fieldset/div/div/div[1]/div/div/div[3]/ul/li[4]'
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, hour))).click()

    send = '/html/body/div[1]/div/div/div[3]/div/div/div[2]/main/div[2]/div/div/div[1]/div[2]/div/div[2]/ul/li/div/div[2]/form/div[2]/div/button[1]'
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, send))).click()
    return


def get_link_ID_title(elem):
    link = elem.get_attribute('href')
    title = elem.find_element(By.XPATH, './span[2]').get_attribute('title')
    match = re.findall("/[0-9]+-", link)
    ID = match[0][1:-1]
    return link, ID, title


def get_matches_info(champ_title, data):
    sleep(2)
    try: # dashboard contenente le info e le quote delle partite
        betting_main_dashboard = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CLASS_NAME, 'betting-main-dashboard')))
        ui_dashboard_champs = WebDriverWait(betting_main_dashboard, 20).until(EC.presence_of_all_elements_located((By.XPATH, './div/ul/li')))

        ui_dashboard_champ = ui_dashboard_champs[0] #for loop check(?)

        ui_dashboard_champ_head = WebDriverWait(ui_dashboard_champ, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-dashboard-champ__head')))
    except:
        print(f'\nEXCEPTION: Riscontrato problema nel trovare alcuni elementi nella dashboard con le info e le quote delle partite.')
        return False

    try:    
        champ_title_match = ui_dashboard_champ_head.find_element(By.XPATH, './div[1]/a/span[2]/span').text
        first_quote = ui_dashboard_champ_head.find_element(By.XPATH, './div[2]/span[1]/span[1]/span').text
    except:
        print(f'\nEXCEPTION: Riscontrato problema nel trovare il nome del campionato o il tipo di quotazione.')
        return False

    if champ_title != champ_title_match: # se il nome del campionato non coincide con quello richiesto
        print('\nEXCEPTION: Campionato selezionato e campionato visualizzato non corrispondono.')
        print(f'{champ_title}   !=   {champ_title_match}')
        print(f'link: {data[0]}')
        return False
    elif first_quote != '1': # se la prima quota non è 1
        print('\nEXCEPTION: Le quote non sono del tipo 1X2.')
        return False
        
    matches = WebDriverWait(ui_dashboard_champ, 20).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
    for match in matches:
        class_type = match.get_attribute('class')
        if class_type == 'ui-dashboard-date': continue # se è una data non mi interessa

        try: # nomi dei team
            teams = match.find_element(By.XPATH, './div[1]/span[1]/a/span/span')
            team1 = teams.find_element(By.XPATH, './div[1]/div[1]/span/span').text      #'./div[1]/div[1]/span[2]/span'
            team2 = teams.find_element(By.XPATH, './div[2]/div[1]/span/span').text      #'./div[2]/div[1]/span[2]/span'
        except:
            print(f'\nEXCEPTION: Impossibile trovare le squadre sfidanti.')
            continue

        try: # quotazioni 1X2
            match_quotations = match.find_element(By.XPATH, './div[2]/span[1]')
            quotation1 = match_quotations.find_element(By.XPATH, './button[1]/span').text
            quotationX = match_quotations.find_element(By.XPATH, './button[2]/span').text 
            quotation2 = match_quotations.find_element(By.XPATH, './button[3]/span').text
        except:
            print(f'\nEXCEPTION: Impossibile trovare le quotazioni per la partita {team1} - {team2}.')
            continue
        
        try: # data e orario/tempo
            time = match.find_element(By.XPATH, './div[1]/span[2]/span[1]')
            if live:
                date = f'{datetime.now().day}/{datetime.now().month}'
                hour = time.find_element(By.XPATH, './span[1]').text
                QUOTATIONS_LIVE.append(f'{data[1]},{champ_title},{team1},{team2},{date},{hour},{quotation1},{quotationX},{quotation2},{data[0]}')
            else:
                date = time.find_element(By.XPATH, './span[1]').text
                hour = time.find_element(By.XPATH, './span[2]').text
                QUOTATIONS_LINE.append(f'{data[1]},{champ_title},{team1},{team2},{date},{hour},{quotation1},{quotationX},{quotation2},{data[0]}')
    
            print(f'\n{champ_title}')
            print(f'{team1}   vs   {team2}')
            print(f'Date: {date}    Time: {hour}')
            print(f'1: {quotation1}    X: {quotationX}    2: {quotation2}')
        except:
            print(f"\nEXCEPTION: Impossibile trovare la data e l'orario per la partita {team1} - {team2}.")
            date = f'{datetime.now().day}/{datetime.now().month}'
            hour = '-'
            if live: QUOTATIONS_LIVE.append(f'{data[1]},{champ_title},{team1},{team2},{date},{hour},{quotation1},{quotationX},{quotation2},{data[0]}')
            else: QUOTATIONS_LINE.append(f'{data[1]},{champ_title},{team1},{team2},{date},{hour},{quotation1},{quotationX},{quotation2},{data[0]}')
    return True


def parse():
    sleep(5) ##

    if not live: apply_filter()
    # menù 'Sport'
    sport_menu = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CLASS_NAME, 'sports-menu')))
    sleep(5) ##
    sports_menu_group = WebDriverWait(sport_menu, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'sports-menu-content__inner')))
    sports_menu_content_section = WebDriverWait(sports_menu_group, 30).until(EC.presence_of_element_located((By.XPATH, './div[1]/div'))) #da riguardare(?)
    n = 1
    test_title = sports_menu_content_section.get_attribute('title')
    if test_title: n = 2
    championships = WebDriverWait(sports_menu_group, 20).until(EC.presence_of_all_elements_located((By.XPATH, f'./div[{n}]/nav/ul/li[1]/ul/li')))
    print(f'Championships n: {len(championships)}') ##

    championships_links = []
    for ch in championships:
        champ = WebDriverWait(ch, 30).until(EC.element_to_be_clickable((By.XPATH, './div')))
        champ_title = champ.get_attribute('title')
        if champ_title:
            print(champ_title) ##
            champ.location_once_scrolled_into_view
            champ.click()
            subchampionships = WebDriverWait(ch, 20).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li/div')))
            for sub_champ in subchampionships:
                sub_champ_elem = sub_champ.find_element(By.XPATH, './a')
                link, ID, sub_champ_title = get_link_ID_title(sub_champ_elem)
                data = (link, ID, sub_champ_title)
                if champ_title not in TO_SKIP: championships_links.append(data)
                print(f'{sub_champ_title}: {link}') ##
            champ.click()
        else:
            champ_elem = champ.find_element(By.XPATH, './a')
            link, ID, champ_title = get_link_ID_title(champ_elem)
            data = (link, ID, champ_title)
            if champ_title not in TO_SKIP: championships_links.append(data)
            print(f'{champ_title}: {link}') ##
        
    print(championships_links)

    for data in championships_links:
        link = data[0]
        champ_title = data[2]
        if champ_title not in TO_SKIP:
            driver.get(link)
            sleep(5) ###
            if not live: apply_filter()
            parse = get_matches_info(champ_title, data)
            if not parse: print('Problema nel reperire i dati.')

    # scrive file delle quote
    if live: ext = 'live'
    else: ext = 'line'
    with open(f'{ext}_{date_time}.csv', 'w') as quotations: #, encoding="utf-8"
        if live:
            for qt in QUOTATIONS_LIVE:
                quotations.write(f'{qt}\n')
        else:
            for qt in QUOTATIONS_LINE:
                quotations.write(f'{qt}\n')
        quotations.close()

    print(f'\nFile {ext}_{date_time}.csv completato.\n') ##

    return


now = datetime.now()
date_time = now.strftime('%Y%m%d_%H%M')

'''
# live parsing
live = True
driver.get(live_matches)
driver.maximize_window()
parse()
'''
# line parsing
live = False
driver.get(line_matches)
driver.maximize_window()
parse()

driver.close()