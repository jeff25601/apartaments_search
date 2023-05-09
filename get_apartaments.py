from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium import webdriver
import time
import pandas as pd
import numpy as np

def get_apartaments(num_apartaments):

    # Initialize the webdriver
    options = webdriver.ChromeOptions()

    #Change the path to where chromedriver is in your home folder
    driver = webdriver.Chrome(options = options)

    url = 'https://www.vivareal.com.br/aluguel/minas-gerais/belo-horizonte/apartamento_residencial/#onde=Brasil,Minas%20Gerais,Belo%20Horizonte,,,,,,BR%3EMinas%20Gerais%3ENULL%3EBelo%20Horizonte,,,'
    driver.get(url)

    apartaments = []
    time.sleep(10)
    try:
        driver.find_element_by_class_name('cookie-notifier__cta').click()
    except NoSuchElementException:
        print("Scraping terminated before reaching target number of apartaments. Needed {}, got {}.".format(num_apartaments, len(apartaments)))
        return



    while len(apartaments) < num_apartaments:
        time.sleep(1)

        indexes = np.arange(0, 36)

        for index in indexes:
            print("Progress: {}".format("" + str(len(apartaments)) + "/" + str(num_apartaments)))
            if len(apartaments) >= num_apartaments:
                break
            try:
                page = driver.find_element_by_css_selector('div[data-index="' + str(index) + '"]')

                try:
                    location = page.find_element_by_xpath('.//span[@class="property-card__address"]').text
                except NoSuchElementException:
                    try:
                        page.find_element_by_class_name('ins-element-content').click()
                        location = page.find_element_by_xpath('.//span[@class="property-card__address"]').text
                    except NoSuchElementException or StaleElementReferenceException:
                        location = -1
                
                try: 
                    detalhes = page.find_element_by_class_name('property-card__details').text
                except NoSuchElementException:
                    try: 
                        page.find_element_by_class_name('ins-element-content').click()
                        detalhes = page.find_element_by_class_name('property-card__details').text
                    except NoSuchElementException or StaleElementReferenceException:
                        detalhes = "-1\n-1\n-1\n-1"

                area = detalhes.split('\n')[0]
                quartos = detalhes.split('\n')[1]
                banheiros = detalhes.split('\n')[2]
                garagem = detalhes.split('\n')[3]

                try: 
                    aluguel = page.find_element_by_tag_name('p').text
                except NoSuchElementException:
                    try:
                        page.find_element_by_class_name('ins-element-content').click()
                        aluguel = page.find_element_by_tag_name('p').text
                    except NoSuchElementException or StaleElementReferenceException:
                        aluguel = -1

                try: 
                    condominio = page.find_element_by_tag_name('footer').text
                except NoSuchElementException:
                    try:
                        page.find_element_by_class_name('ins-element-content').click()
                        condominio = page.find_element_by_tag_name('footer').text
                    except NoSuchElementException or StaleElementReferenceException:
                        condominio = -1
                
                try:
                    link = page.find_element_by_tag_name('a').get_attribute('href')
                except NoSuchElementException:
                    try:
                        page.find_element_by_class_name('ins-element-content').click()
                        link = page.find_element_by_tag_name('a').get_attribute('href')
                    except NoSuchElementException or StaleElementReferenceException:
                        link = -1
                
                try: 
                    page.find_element_by_tag_name('a').click()
                    driver.switch_to.window(driver.window_handles[1])
                    time.sleep(1)
                    iptu = driver.find_element_by_class_name('price__list-value.iptu.js-iptu').text
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except NoSuchElementException:
                    try:
                        page.find_element_by_class_name('ins-element-content').click()
                        page.find_element_by_tag_name('a').click()
                        driver.switch_to.window(driver.window_handles[1])
                        time.sleep(1)
                        iptu = driver.find_element_by_class_name('price__list-value iptu js-iptu').text
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except NoSuchElementException or StaleElementReferenceException:
                        iptu = -1

            except NoSuchElementException:
                location = -1
                area = -1
                quartos = -1
                banheiros = -1
                garagem = -1
                aluguel = -1
                condominio = -1
                link = -1 
                iptu = -1       
            
            apartaments.append({"local": location,
                                "area": area,
                                "quartos": quartos,
                                "banheiros": banheiros,
                                "vagas_garagem": garagem,
                                "aluguel": aluguel,
                                "condominio": condominio,
                                "iptu": iptu,
                                "url": link})
        
        try:
            driver.find_element_by_css_selector('button[title="Próxima página"]').click()
        except NoSuchElementException:
            print("Scraping terminated before reaching target number of apartaments. Needed {}, got {}.".format(num_apartaments, len(apartaments)))
            break
    return pd.DataFrame(apartaments)

data = get_apartaments(4500)

data = data.drop_duplicates()

data = data[data['local'] != -1]

data.to_excel("apartamentos.xlsx")

data = pd.read_excel("apartamentos.xlsx", index_col=None)



data["rua"] = data['local'].apply(lambda x: x.split(" - ")[0] if "Rua" in x or "Avenida" in x else "")

data["bairro"] = data['local'].apply(lambda x: x.split(" - ")[1] if "Rua" in x or "Avenida" in x else x.split("-")[0])

data['bairro'] = data['bairro'].apply(lambda x: x.split(", ")[0])

data['area'] = data['area'].apply(lambda x: int(x.split(" ")[0]))

data['quartos'] = data['quartos'].apply(lambda x: int(x.split(" ")[0]))

data['banheiros'] = data['banheiros'].apply(lambda x: int(x.split(" ")[0]))

data['vagas_garagem'] = data['vagas_garagem'].apply(lambda x: int(x.split(" ")[0]) if "--" not in x else 0)

data['aluguel'] = data['aluguel'].apply(lambda x: int(x.split(" ")[1].replace(".", "")))

data['condominio'] = data['condominio'].apply(lambda x: int(x.split(" ")[2].replace(".", "")) if x != -1 else -1)

data = data.drop(columns=['Unnamed: 0', 'local'])

data = data[['rua', 'bairro', 'area', 'quartos', 'banheiros', 'vagas_garagem', 'aluguel', 'condominio']]



data.to_excel("apartamentos_tratado.xlsx", index = False)