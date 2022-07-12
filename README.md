
# Updater for [coronaviruslive.it](https://coronaviruslive.it)
![Checking for updates...](https://github.com/Sasso0101/coronavirus-updater/workflows/Checking%20for%20updates.../badge.svg)

This Docker container updates [coronaviruslive.it](https://coronaviruslive.it) by checking data sources every 5 minutes.

#### Data sources
|Data|Source  |
|--|--|
| 🦠 Covid-19 | https://github.com/pcm-dpc/COVID-19 |
| 💉 Vaccines | https://github.com/italia/covid19-opendata-vaccini |

## Build 
Clone the repository and run the following commands:

	cd container
	docker build -t coronavirus-updater .

## Deploy 
Create a file named .env in the project's directory with the following content:

	FTPHOST = "FTP server url"
	FTPUSER = "FTP username"
	FTPPASSWORD = "FTP password"
	PUSHAUTH = "Onesignal (Can be found here: https://app.onesignal.com/profile)"
	PUSHID = "Onesignal API key (Project > Settings > Keys & IDs)"
	TELEGRAMID = "Telegram bot key"
	FACEBOOKTOKEN = "Facebook account token"
	FACEBOOKID = "Facebook page ID"

Run the following commands:

    docker-compose up -d
