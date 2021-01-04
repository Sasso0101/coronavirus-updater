''' Helper functions to retrieve, parse and update covid19 data released by the italian govt '''

import pandas, os, io, requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from ftplib import FTP
from github import Github
from pytz import timezone
load_dotenv()
currentPath = str(Path(__file__).parent)+'/'

def getData(url, duplicatesSubset = False):
    ''' Returns CSV parsed object '''
    decodedCSV = pandas.read_csv(url)
    
    # Removes duplicates
    if duplicatesSubset:
        decodedCSV.drop_duplicates(subset = duplicatesSubset, keep = False, inplace = True) 
    decodedCSV = decodedCSV.to_dict('records')
    return decodedCSV

def getLatestTotal(nationalData):
    ''' Returns total of everything from last day for comparison '''
    return nationalData[-1]['totale_positivi'] + nationalData[-1]['dimessi_guariti'] + nationalData[-1]['deceduti'] + nationalData[-1]['tamponi']

def somethingChanged(nationalData):
    ''' Checks if downladed latest total is different from saved one
        If True updates saved total '''
    latestTotal = getLatestTotal(nationalData)
    latestSavedTotal = requests.get('https://salvatoreandaloro.altervista.org/coronavirus/latestTotal.txt')
    latestSavedTotal = int(latestSavedTotal.text)
    if latestTotal == latestSavedTotal: return False
    else:
        print('Total: ' + str(latestTotal))
        with FTP(os.environ['FTPHOST'], os.environ['FTPUSER'], os.environ['FTPPASSWORD']) as ftp:
            ftpFile = io.BytesIO(str(latestTotal).encode("utf-8"))
            ftp.storbinary(f'STOR {"coronavirus/latestTotal.txt"}', ftpFile)
        return True

def getChartDataNewCases(nationalData):
    ''' Returns formatted array for chartJS with updated new cases '''
    chart = [
        [],
        ["Nuovi positivi", "#bc8500"],
        ["Nuovi decessi", "#f11806"],
        ["Nuovi guariti", "#228200"],
        ["Tamponi eseguiti", "#adadad"],
    ]

    #Default values
    totalRecoveredPreviousDay = 0
    totalDeathsPreviousDay = 1
    totalTestsPreviousDay = 0

    #Fill chart data day by day
    for day in nationalData:
        dataDatetime = datetime.strptime(day['data'], '%Y-%m-%dT%H:%M:%S')
        chart[0].append(dataDatetime.strftime("%d/%m/%Y")) #Date
        chart[1].append(day['nuovi_positivi']) #New active cases
        chart[2].append(day['deceduti'] - totalDeathsPreviousDay) #New deaths
        chart[3].append(day['dimessi_guariti'] - totalRecoveredPreviousDay) #New revocered
        chart[4].append(day['tamponi'] - totalTestsPreviousDay) #New tests
        totalRecoveredPreviousDay = day['dimessi_guariti']
        totalDeathsPreviousDay = day['deceduti']
        totalTestsPreviousDay = day['tamponi']
    return chart

def getChartActiveCases(nationalData):
    ''' Returns formatted array for chartJS with stuatus of active cases day by day '''
    chart = [
        [],
        ["In terapia intensiva", "#ff1900", "#870d00"],
        ["Altri ospedalizzati", "#008abc", "#005270"],
        ["Isolamento domiciliare", "#bc8500", "#8c6300"],
    ]

    #Fill chart data day by day
    for day in nationalData:
        dataDatetime = datetime.strptime(day['data'], '%Y-%m-%dT%H:%M:%S')
        chart[0].append(dataDatetime.strftime("%d/%m/%Y"))
        chart[1].append(day['terapia_intensiva'])
        chart[2].append(day['totale_ospedalizzati'] - day['terapia_intensiva'])
        chart[3].append(day['isolamento_domiciliare'])
    return chart

def getChartCumulativeCases(nationalData):
    ''' Returns formatted array for chartJS with cumulative cases '''
    chart = [
        [],
        ["Decessi", "#f11806", "#990c00"],
        ["Attualmente positivi", "#bc8500", "#8c6300"],
        ["Guariti", "#228200", "#195e00"],
    ]

    #Fill chart data day by day
    for day in nationalData:
        dataDatetime = datetime.strptime(day['data'], '%Y-%m-%dT%H:%M:%S')
        chart[0].append(dataDatetime.strftime("%d/%m/%Y"))
        chart[1].append(day['deceduti'])
        chart[2].append(day['totale_positivi'])
        chart[3].append(day['dimessi_guariti'])
    return chart

def getDayData(nationalData, day):
    ''' Parses requested day from now data and returns parsed python object '''
    today = {
        'activeCases': nationalData[-day]['totale_positivi'],
        'newActiveCases': nationalData[-day]['nuovi_positivi'],
        'recovered': nationalData[-day]['dimessi_guariti'],
        'newRecovered': nationalData[-day]['dimessi_guariti'] - nationalData[-day-1]['dimessi_guariti'],
        'selfIsolation': nationalData[-day]['isolamento_domiciliare'],
        'hospitalized': nationalData[-day]['totale_ospedalizzati'],
        'diffHospitalized': nationalData[-day]['totale_ospedalizzati'] - nationalData[-day-1]['totale_ospedalizzati'],
        'intensiveCare': nationalData[-day]['terapia_intensiva'],
        'diffIntensiveCare': nationalData[-day]['terapia_intensiva'] - nationalData[-day-1]['terapia_intensiva'],
        'deaths': nationalData[-day]['deceduti'],
        'newDeaths': nationalData[-day]['deceduti'] - nationalData[-day-1]['deceduti'],
        'tests': nationalData[-day]['tamponi'],
        'newTests': nationalData[-day]['tamponi'] - nationalData[-day-1]['tamponi'],
        'peopleTested': nationalData[-day]['casi_testati'],
        'newPeopleTested': nationalData[-day]['casi_testati'] - nationalData[-day-1]['casi_testati'],
    }
    return today

def getRegionsData(regionsData, regionsDataYesterday):
    ''' Parses regions file and returns parsed python object '''
    regions = []
    for region in regionsData:
        yesterday = findObject(regionsDataYesterday, region['codice_regione'], 'region')
        regions.append({
            'code': region['codice_regione'],
            'name': region['denominazione_regione'],
            'activeCases': region['totale_positivi'],
            'newActiveCases': region['nuovi_positivi'],
            'recovered': region['dimessi_guariti'],
            'newRecovered': region['dimessi_guariti'] - yesterday['dimessi_guariti'],
            'hospitalized': region['totale_ospedalizzati'],
            'intensiveCare': region['terapia_intensiva'],
            'deaths': region['deceduti'],
            'newDeaths': region['deceduti'] - yesterday['deceduti'],
            'tests': region['tamponi'],
            'newTests': region['tamponi'] - yesterday['tamponi'],
            'peopleTested': region['casi_testati'],
            'newPeopleTested': region['casi_testati'] - yesterday['casi_testati'],
        })
    return regions

def mergeTST(regionsData):
    ''' Merge Trento and Bozen provinces into one single region
        Returns region list with new region and with both provinces removed '''
    bozen = findObject(regionsData, 21, 'region')
    trento = findObject(regionsData, 22, 'region')
    region = {
        'codice_regione': 4,
        'denominazione_regione': 'Trentino-Alto Adige/Südtirol',
        'totale_positivi': bozen['totale_positivi'] + trento['totale_positivi'],
        'nuovi_positivi': bozen['nuovi_positivi'] + trento['nuovi_positivi'],
        'dimessi_guariti': bozen['dimessi_guariti'] + trento['dimessi_guariti'],
        'totale_ospedalizzati': bozen['totale_ospedalizzati'] + trento['totale_ospedalizzati'],
        'terapia_intensiva': bozen['terapia_intensiva'] + trento['terapia_intensiva'],
        'deceduti': bozen['deceduti'] + trento['deceduti'],
        'tamponi': bozen['tamponi'] + trento['tamponi'],
        'casi_testati': bozen['casi_testati'] + trento['casi_testati'],
    }
    regionsData.remove(bozen)
    regionsData.remove(trento)
    regionsData.append(region)
    return regionsData

def findObject(data, code, dataType):
    ''' Finds province or region by provided code and returns its object '''
    for dataObject in data:
        if dataType == 'region':
            if dataObject['codice_regione'] == code:
                return dataObject
        if dataType == 'province':
            if dataObject['codice_provincia'] == code:
                return dataObject

def getProvincesData(provincesData, provincesDataYesterday, provincesData30DaysAgo):
    ''' Parses provinces file and returns parsed python object '''
    provinces = []
    for province in provincesData:
        # Don't count out of region/unknown cases
        if province['codice_provincia'] < 879:
            totalCasesYesterday = findObject(provincesDataYesterday, province['codice_provincia'], 'province')['totale_casi']
            totalCasesToday = province['totale_casi'] - totalCasesYesterday
            if totalCasesToday < 0:
                totalCasesToday = 0
            totalCases30DaysAgo = findObject(provincesData30DaysAgo, province['codice_provincia'], 'province')['totale_casi']
            provinces.append({
                'code': province['codice_provincia'],
                'name': province['denominazione_provincia'],
                'totalCases': province['totale_casi'],
                'totalCasesToday': totalCasesToday,
                'totalCasesLast30Days': province['totale_casi'] - totalCases30DaysAgo
            })
    return provinces

def uploadData(fileName, data):
    ''' Creates dummy file with php header and JSON data and uploads it to remote server via FTP '''
    data = '<?php header("Access-Control-Allow-Origin: *");header("Content-Type: application/json");?>' + data
    with FTP(os.environ['FTPHOST'], os.environ['FTPUSER'], os.environ['FTPPASSWORD']) as ftp:
        ftpFile = io.BytesIO(data.encode('utf-8'))
        ftp.storbinary(f'STOR {fileName}', ftpFile)
    print("File uploaded!")

def getLatestCommitDatetime():
    ''' Returns latest commit datetime on andamento-nazionale-latest.csv '''
    g = Github()
    repo = g.get_repo("pcm-dpc/COVID-19")
    commits = repo.get_commits(path='dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale-latest.csv')
    if commits.totalCount:
        utc = timezone('UTC')
        rome = timezone('Europe/Rome')
        localized = utc.localize(commits[0].commit.committer.date)
        return localized.astimezone(rome)

def getVaccineData():
    ''' Returns latest vaccine data in form of array '''
    vaccineData = requests.get('https://salvatoreandaloro.altervista.org/coronavirus/5G.php')
    return vaccineData.json()