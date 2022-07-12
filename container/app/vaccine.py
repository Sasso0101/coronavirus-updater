from datetime import datetime
import json
from updateData import *

data = getData("https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/vaccini-summary-latest.csv")
vaccinated = 0
availableVaccines = 0
for region in data:
    vaccinated += int(region['dosi_somministrate'])
    availableVaccines += int(region['dosi_consegnate'])
    
lastUpdated = getLatestCommitDatetime('italia/covid19-opendata-vaccini', 'dati/vaccini-summary-latest.csv')
lastUpdated = lastUpdated.strftime("%H:%M %d/%m/%Y")
jsonString = {
    "vaccinated": vaccinated,
    "availableVaccines": availableVaccines,
    "lastUpdated": lastUpdated
}
jsonString = json.dumps(jsonString)
uploadData("coronavirus/5G.php", jsonString)