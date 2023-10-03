from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
import re


QUOTATIONS_LIVE = ['ID,Championship,Team1,Team2,Date,Current_Time,1,X,2,Link']
QUOTATIONS_LINE = ['ID,Championship,Team1,Team2,Date,Hour,1,X,2,Link']

service = Service(r'./geckodriver')
driver = Firefox(service = service)


# applicazione filtro 12h
def apply_filter():
    return


def get_matches_info(live, data):
    try: # dashboard contenente le info e le quote delle partite
        betting_main_dashboard = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CLASS_NAME, 'betting-main-dashboard')))
        ui_dashboard_champs = WebDriverWait(betting_main_dashboard, 20).until(EC.presence_of_all_elements_located((By.XPATH, './div/ul/li')))

        ui_dashboard_champ = ui_dashboard_champs[0] #for loop check(?)

        ui_dashboard_champ_head = WebDriverWait(ui_dashboard_champ, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-dashboard-champ__head')))
    except:
        print(f'\nEXCEPTION: Riscontrato problema nel trovare alcuni elementi nella dashboard con le info e le quote delle partite.')
        return False

    try:
        champ_title = WebDriverWait(ui_dashboard_champ_head, 20).until(EC.presence_of_element_located((By.XPATH, './div[1]/a/span[2]/span'))).text
        first_quote = WebDriverWait(ui_dashboard_champ_head, 20).until(EC.presence_of_element_located((By.XPATH, './div[2]/span[1]/span[1]/span'))).text
    except:
        print(f'\nEXCEPTION: Riscontrato problema nel trovare il nome del campionato o il tipo di quotazione.')
        return False

    if first_quote != '1': # se la prima quota non è 1
        print('\nEXCEPTION: Le quote non sono del tipo 1X2.')
        return False
        
    matches = WebDriverWait(ui_dashboard_champ, 20).until(EC.presence_of_all_elements_located((By.XPATH, './ul/li')))
    for match in matches:
        class_type = match.get_attribute('class')
        if class_type == 'ui-dashboard-date': continue # se è una data non mi interessa

        try: # nomi dei team
            teams = WebDriverWait(match, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'team-scores__top')))
            team1 = WebDriverWait(teams, 20).until(EC.presence_of_element_located((By.XPATH, './span/div[1]/div[1]/span/span'))).text
            team2 = WebDriverWait(teams, 20).until(EC.presence_of_element_located((By.XPATH, './span/div[2]/div[1]/span/span'))).text
        except:
            print(f'\nEXCEPTION: Impossibile trovare le squadre sfidanti.')
            continue

        try: # quotazioni 1X2
            match_quotations = WebDriverWait(match, 20).until(EC.presence_of_element_located((By.XPATH, './div[2]/span[1]')))
            quotation1 = WebDriverWait(match_quotations, 20).until(EC.presence_of_element_located((By.XPATH, './button[1]/span'))).text
            quotationX = WebDriverWait(match_quotations, 20).until(EC.presence_of_element_located((By.XPATH, './button[2]/span'))).text
            quotation2 = WebDriverWait(match_quotations, 20).until(EC.presence_of_element_located((By.XPATH, './button[3]/span'))).text
        except:
            print(f'\nEXCEPTION: Impossibile trovare le quotazioni per la partita {team1} - {team2}.')
            continue
        
        try: # data e orario/tempo
            time = WebDriverWait(match, 20).until(EC.presence_of_element_located((By.XPATH, './div[1]/span[2]/span[1]')))
            if live:
                date = f'{datetime.now().day}/{datetime.now().month}'
                hour = WebDriverWait(time, 20).until(EC.presence_of_element_located((By.XPATH, './span[1]'))).text
                QUOTATIONS_LIVE.append(f'{data[1]},{champ_title},{team1},{team2},{date},{hour},{quotation1},{quotationX},{quotation2},{data[0]}')
            else:
                date = WebDriverWait(time, 20).until(EC.presence_of_element_located((By.XPATH, './span[1]'))).text
                hour = WebDriverWait(time, 20).until(EC.presence_of_element_located((By.XPATH, './span[2]'))).text
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


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parse arguments for a script')
    parser.add_argument('-o', '--option', choices=['line', 'live'], required=False, help='Option')
    parser.add_argument('-l', '--link', required=True, help="The page's link to parse")
    args = parser.parse_args()
    
    match = re.findall('/[0-9]+-', args.link)
    id = match[0][1:-1]

    try:
        live = True if 'live' in args.link else False
    except:
        if args.option is not None:
            live = True if args.option == 'live' else False
        else:
            print("Option 'live'/'line' not given")
            return

    if live: print('Option: live')
    else: print('Option: line')
    print(f'Parsed link: {args.link}')
    print(f'Match ID: {id}')

    now = datetime.now()
    date_time = now.strftime('%Y%m%d_%H%M')

    driver.get(args.link)
    driver.maximize_window()
    #if not live: apply_filter()
    parse = get_matches_info(live, (args.link, id))
    if not parse: return

    # scrive file delle quote
    if live: ext = 'live'
    else: ext = 'line'
    with open(f'{ext}_{id}_quotations_{date_time}.csv', 'w', encoding="utf-8") as quotations:
        if live:
            for qt in QUOTATIONS_LIVE:
                quotations.write(f'{qt}\n')
        else:
            for qt in QUOTATIONS_LINE:
                quotations.write(f'{qt}\n')
        quotations.close()

    print(f'\nFile {ext}_quotations_{date_time}.csv completato.\n') ##
    driver.close()
    return


if __name__ == "__main__":
    main()
