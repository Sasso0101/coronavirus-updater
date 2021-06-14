from bs4 import BeautifulSoup
import json
import requests
from updateData import uploadData

website = requests.get(
    'https://www.governo.it/it/articolo/domande-frequenti-sulle-misure-adottate-dal-governo/15638')
soup = BeautifulSoup(website.text, 'html.parser')

ids = {
    "friuliveneziagiulia": "", "veneto": "", "trento": "", "bolzano": "", "lombardia": "", "piemonte": "", "valledaosta": "", "liguria": "", "emiliaromagna": "", "toscana": "", "marche": "", "umbria": "", "lazio": "", "campania": "", "abruzzo": "", "molise": "", "puglia": "", "basilicata": "", "calabria": "", "sicilia": "", "sardegna": ""
}

colors = []
for id in ids:
    color = soup.find(id=id)['fill']
    ids[id] = color

jsonString = json.dumps(ids)
uploadData("coronavirus/zones.php", jsonString)