from logging import lastResort
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import json
import pathlib
from updateData import uploadData

chromeOptions = Options()
chromeOptions.add_argument('--headless')
chromeOptions.add_argument("--remote-debugging-port=9222")
chromeOptions.add_argument('--no-sandbox')
path = str(pathlib.Path(__file__).parent.absolute())+'/chromedriver'
driver = webdriver.Chrome(path, options=chromeOptions)
try:
    driver.get("https://app.powerbi.com/view?r=eyJrIjoiMzg4YmI5NDQtZDM5ZC00ZTIyLTgxN2MtOTBkMWM4MTUyYTg0IiwidCI6ImFmZDBhNzVjLTg2NzEtNGNjZS05MDYxLTJjYTBkOTJlNDIyZiIsImMiOjh9")
    element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".bodyCells > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)"))
        )
    vaccinated = 0
    availableVaccines = 0
    for region in range(1, 21):
        vaccinated += int(driver.find_element_by_css_selector(".bodyCells > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(" + str(region) + ")").text.replace('.', ''))
        pass
    vaccinated += int(driver.find_element_by_css_selector(".bodyCells > div > div:nth-child(2) > div:nth-child(1)").text.replace('.', ''))
    for region in range(1, 21):
        availableVaccines += int(driver.find_element_by_css_selector(".bodyCells > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(" + str(region) + ")").text.replace('.', ''))
        pass
    availableVaccines += int(driver.find_element_by_css_selector(".bodyCells > div > div:nth-child(2) > div:nth-child(2)").text.replace('.', ''))

    lastUpdated = driver.find_element_by_css_selector(".title:nth-of-type(1)")
    lastUpdated = datetime.strptime(lastUpdated.text, '%d/%m/%Y %H:%M:%S')
    lastUpdated = lastUpdated.strftime("%H:%M %d/%m/%Y")
    jsonString = {
        "vaccinated": vaccinated,
        "availableVaccines": availableVaccines,
        "lastUpdated": lastUpdated
    }
    jsonString = json.dumps(jsonString)
    uploadData("coronavirus/5G.php", jsonString)
finally:
    driver.close()