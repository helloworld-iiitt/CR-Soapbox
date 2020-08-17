<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://raw.githubusercontent.com/DattatreyaReddy/datta_repo/master/CR_ALT_LOGO.jpg?token=AOABVVCATGPHLKQIM4EOMK27HK5LS" alt="Bot logo"></a>
</p>

<h3 align="center">CR SOAPBOX</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Platform](https://img.shields.io/badge/platform-reddit-orange.svg)](https://t.me/CR_ALT_BOT)
[![GitHub Issues](https://img.shields.io/github/issues/helloworld-iiitt/CR-Soapbox)](https://github.com/helloworld-iiitt/CR-Soapbox/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/helloworld-iiitt/CR-Soapbox)](https://github.com/helloworld-iiitt/CR-Soapbox/pulls)

</div>

---

<p align="center">  CR SOAPBOX is a personalized TIME TABLE Manager for IIITT Students and Teachers. 
By registering with your IIITT ROLL No or Email ID , you can get the Personalized 
Daily time table, Bunk manager(for Students ) , Can Make Changes in Timetable (for Teachers) 
and many more. It's totally an alternative for Class representative
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [How it works](#working)
- [Usage](#usage)
- [Getting Started](#getting_started)
- [Deploying your own bot](#deployment)
- [Built Using](#built_using)
- [TODO](../TODO.md)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

CR SOAPBOX is an alternative for Class Representative 😉.

Students:

- Can get timetable (Up-to-date).
- Can set & get attendance (Bunk manager).
- Can receive announcements (Creation and Deletion of classes, Messages, Files, Polls, etc.).

Teachers:

- Can get personal and grade timetables (Up-to-date).
- Can modify timetable (Create and Cancel classes).
- Can make announcements (messages,polls,files, etc.)

## 💭 How it works <a name = "working"></a>

- By starting the server the bot will fetch the timetable and other details from the json files in the project.

- The bot uses the Telegram API to fetch messages, Python Telegram Bot module to reply to messages and IIITT server as a server.

- The entire bot is written in Python 3.8

## 🎈 Usage <a name = "usage"></a>

Start the bot by sending :

```
    /start
```

- The bot will ask the user whether he is a student or teacher.

Student:

- Bot will ask the user to send the IIITT Roll no to log in.
- The bot first extracts the grade from the users roll no, process it and store it in database.
- if the roll no does not exists then it will send an error message.
- Then the bot will responds according to the student's requests.

Here is the demo of Students
![Working](https://media.giphy.com/media/20NLMBm0BkUOwNljwv/giphy.gif)

Teachers:

- Bot will ask the user to send his IIITT Mail address to log in.
- The bot will check if the user entered email id is of teachers from IIITT.
- if it not belongs to a teacher from IIITT it will through an error
- Then the bot will responds according to the teacher's requests.

Hear is the demo of Teachers
![Working](https://media.giphy.com/media/20NLMBm0BkUOwNljwv/giphy.gif)

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

You can find the required python modules in requirments.txt file:

```
  python-telegram-bot
  pytz
```

You can install these modules by running this command in terminal:

```
  pip3 install -r requirements.txt
```

### **Installing**
1. Clone the repository:

```
  git clone https://github.com/DattatreyaReddy/CR-Soapbox.git
  cd CR-Soapbox/
```
2. Head to data/bottkn.txt and replace the text with the bot token from [@botfather](https://core.telegram.org/bots#6-botfather) in telegram

3. 
- To Deploy the bot with polling ignore this step (good for initial development)
- To Deploy the bot with webhook refer [Python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks) (Good for server deployment)

4. Add executable permissions start.sh file and run it:
```
  chmod +x start.sh
  ./start.sh
```

- **Heroku**: https://github.com/kylelobo/Reddit-Bot#deploying_the_bot

## ⛏️ Built Using <a name = "built_using"></a>

- [Telegram API](https://core.telegram.org/bots)
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/en/stable/) - Python Telegram API Wrapper

## ✍️ Authors <a name = "authors"></a>

- [@dattatreyareddy](https://github.com/DattatreyaReddy) - Idea & Initial work

See also the list of [contributors](https://github.com/helloworld-iiitt/CR-Soapbox/graphs/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- code - [python-telegram-bot_Code_Snippets](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets) , [pythontelegrambotgroup](https://t.me/pythontelegrambotgroup)
- people - [@anoopjt](https://github.com/anoopjt), [@fahad](https://github.com/fahad-israr)