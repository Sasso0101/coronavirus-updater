import time, json, locale
from pathlib import Path
from datetime import datetime, timedelta
from helpers import *
from updateData import *
from notifications import *

locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

nationalData = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv')

force = isForced()
if somethingChanged(nationalData) or force:
    print('Something changed. Updating...')
    yesterday = datetime.today() - timedelta(days=1)
    yesterday = yesterday.strftime('%Y%m%d')
    regionsData = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv')
    regionsDataYesterday = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-'+yesterday+'.csv')
    daysAgo30 = datetime.today() - timedelta(days=30)
    daysAgo30 = daysAgo30.strftime('%Y%m%d')
    provincesData = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-latest.csv')
    provincesDataYesterday = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-'+yesterday+'.csv')
    provincesData30DaysAgo = getData('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-'+daysAgo30+'.csv')

    data = {}
    data['chartNewCases'] = getChartDataNewCases(nationalData)
    data['chartActiveCases'] = getChartActiveCases(nationalData)
    data['chartCumulativeCases'] = getChartCumulativeCases(nationalData)
    data['today'] = getTodayData(nationalData)
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
    uploadData(json.dumps(data))

    if not notificationSentToday():
        pushTitle = "Nuovi casi coronavirus - Aggiornamento ore 17:00"
        pushMessage = "Dati aggiornati con le informazioni rilasciate dalla Protezione civile alle 17:00."
        sendPushNotification(pushTitle, pushMessage)

        telegramMessage = '<b>Bollettino coronavirus - {}</b>\r\n🟧 {:n} contagi oggi ({:n} attualmente positivi)\r\n🟥 {:n} decessi ({:n} decessi totali)\r\n🟩 {:n} guariti oggi ({:n} guariti totali)\r\n⬜️ {:n} tamponi effettuati oggi ({:n} tamponi totali)\r\n\r\n{:n} in terapia intensiva || {:n} ospedalizzati\r\nVedi i casi nella tua regione su <a href=\"https://coronaviruslive.it\">coronaviruslive.it</a>'.format(now.strftime("%d/%m/%Y"), data['today']['newActiveCases'], data['today']['activeCases'], data['today']['newDeaths'], data['today']['deaths'], data['today']['newRecovered'], data['today']['recovered'], data['today']['newTests'], data['today']['tests'], data['today']['intensiveCare'], data['today']['hospitalized'])
        sendTelegramMessage(telegramMessage)

        facebookMessage = 'Bollettino coronavirus - {}\r\n🟧 {:n} contagi oggi ({:n} attualmente positivi)\r\n🟥 {:n} decessi ({:n} decessi totali)\r\n🟩 {:n} guariti oggi ({:n} guariti totali)\r\n⬜️ {:n} tamponi effettuati oggi ({:n} tamponi totali)\r\n\r\n{:n} in terapia intensiva || {:n} ospedalizzati\r\nVedi i casi nella tua regione su https://coronaviruslive.it'.format(now.strftime("%d/%m/%Y"), data['today']['newActiveCases'], data['today']['activeCases'], data['today']['newDeaths'], data['today']['deaths'], data['today']['newRecovered'], data['today']['recovered'], data['today']['newTests'], data['today']['tests'], data['today']['intensiveCare'], data['today']['hospitalized'])
        sendFacebookMessage(facebookMessage)
else:
    print("Nothing new.")