''' Helper functions to check and send HTML5, Telegram and Facebook notifications '''
import requests, json, os
from datetime import datetime
from pathlib import Path

currentPath = str(Path(__file__).parent)+'/'

def notificationSentToday():
    ''' Check if today the script has alredy sent a notification
        If False assumes we are going to send one and updates date on local file '''
    
    today = datetime.now().strftime("%d/%m/%Y")
    with open(currentPath+'lastNotification.txt', 'r+') as lastNotificationFile:
        lastNotification = lastNotificationFile.read().strip("\n\t ")
        if lastNotification == today: return True
        else:
            lastNotificationFile.seek(0)
            lastNotificationFile.write(today)
            return False

def sendPushNotification(title, message):
    ''' Send HTML5 push notification using Onesignal API
        Returns HTTP response code returned by the API '''
    header = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Basic ' + os.environ['FTPHOST']
    }
    payload = {
        'app_id': os.environ['PUSHID'],
        'included_segments': ['All'],
        'headings': {'en': title},
        'contents': {'en': message},
        'url': 'https://coronaviruslive.it'
    }
    req = requests.post('https://onesignal.com/api/v1/notifications', headers=header, data=json.dumps(payload), verify=False)
    return req.status_code

def sendTelegramMessage(message):
    ''' Send Telegram message
        Returns HTTP response code returned by the API '''
    header = {'Content-Type': 'application/json; charset=utf-8'}
    payload = {
        'chat_id': '@coronavirusliveitalia',
        'text': message,
        'parse_mode': 'HTML',
    }
    req = requests.post('https://api.telegram.org/bot' + os.environ['TELEGRAMID'] + '/sendMessage', headers=header,data=json.dumps(payload), verify=False)
    return req.status_code

def sendFacebookMessage(message):
    access_token = os.environ['FACEBOOKTOKEN']
    header = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
    payload = {
        'access_token': access_token,
        'message': message,
    }
    req = requests.post('https://graph.facebook.com/' + os.environ['FACEBOOKID'] + '/feed', headers=header, data=payload, verify=False)
    return req.status_code
