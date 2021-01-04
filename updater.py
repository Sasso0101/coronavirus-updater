import time, json, locale
from pathlib import Path
from datetime import datetime, timedelta
from helpers import *
from updateData import *
from notifications import *

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

nationalData = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv', 'data')

force = isForced()
if somethingChanged(nationalData) or force:
    print('Something changed. Updating...')
    yesterday = datetime.today() - timedelta(days=1)
    yesterday = yesterday.strftime('%Y%m%d')
    regionsData = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv', 'codice_regione')
    regionsDataYesterday = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-'+yesterday+'.csv', 'codice_regione')
    daysAgo30 = datetime.today() - timedelta(days=30)
    daysAgo30 = daysAgo30.strftime('%Y%m%d')
    provincesData = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-latest.csv', 'codice_provincia')
    provincesDataYesterday = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-'+yesterday+'.csv', 'codice_provincia')
    provincesData30DaysAgo = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-'+daysAgo30+'.csv', 'codice_provincia')

    data = {}
    data['chartNewCases'] = getChartDataNewCases(nationalData)
    data['chartActiveCases'] = getChartActiveCases(nationalData)
    data['chartCumulativeCases'] = getChartCumulativeCases(nationalData)
    data['today'] = getDayData(nationalData, 1)
    data['yesterday'] = getDayData(nationalData, 2)
    regionsData = mergeTST(regionsData)
    regionsDataYesterday = mergeTST(regionsDataYesterday)
    data['regions'] = getRegionsData(regionsData, regionsDataYesterday)
    data['provinces'] = getProvincesData(provincesData, provincesDataYesterday, provincesData30DaysAgo)
    now = datetime.now()
    lastCommit = getLatestCommitDatetime()
    data['lastUpdated'] = {
        'day': lastCommit.strftime("%d/%m/%Y"),
        'time': lastCommit.strftime("%H:%M")
    }
    data['id'] = time.time()
    uploadData("coronavirus/datiV6.php", json.dumps(data))

    if not notificationSentToday():
        vaccineData = getVaccineData()
        pushTitle = "Aggiornamento casi coronavirus"
        pushMessage = "I dati sull'andamento del contagio sono stati aggiornati. Premi per tutte le informazioni."
        sendPushNotification(pushTitle, pushMessage)
        telegramMessage = '<b>Bollettino coronavirus - {}</b>\r\n🟧 {:n} contagi oggi ({:n} attualmente positivi)\r\n🟥 {:n} decessi ({:n} decessi totali)\r\n🟩 {:n} guariti oggi ({:n} guariti totali)\r\n⬜️ {:n} tamponi effettuati oggi ({:n} tamponi totali)\r\n\r\n{:n} in terapia intensiva || {:n} ospedalizzati\r\n\r\n{:n} vaccini somministati (su {:n} dosi disponibili)\r\nVedi i casi nella tua regione su <a href=\"https://coronaviruslive.it\">coronaviruslive.it</a>'.format(now.strftime("%d/%m/%Y"), data['today']['newActiveCases'], data['today']['activeCases'], data['today']['newDeaths'], data['today']['deaths'], data['today']['newRecovered'], data['today']['recovered'], data['today']['newTests'], data['today']['tests'], data['today']['intensiveCare'], data['today']['hospitalized'], vaccineData['vaccinated'], vaccineData['availableVaccines'])
        sendTelegramMessage(telegramMessage)
        facebookMessage = 'Bollettino coronavirus - {}\r\n🟧 {:n} contagi oggi ({:n} attualmente positivi)\r\n🟥 {:n} decessi ({:n} decessi totali)\r\n🟩 {:n} guariti oggi ({:n} guariti totali)\r\n⬜️ {:n} tamponi effettuati oggi ({:n} tamponi totali)\r\n\r\n{:n} in terapia intensiva || {:n} ospedalizzati\r\n\r\n{:n} vaccini somministati (su {:n} dosi disponibili)\r\nVedi i casi nella tua regione su https://coronaviruslive.it'.format(now.strftime("%d/%m/%Y"), data['today']['newActiveCases'], data['today']['activeCases'], data['today']['newDeaths'], data['today']['deaths'], data['today']['newRecovered'], data['today']['recovered'], data['today']['newTests'], data['today']['tests'], data['today']['intensiveCare'], data['today']['hospitalized'], vaccineData['vaccinated'], vaccineData['availableVaccines'])
        sendFacebookMessage(facebookMessage)
else:
    print("Nothing new.")