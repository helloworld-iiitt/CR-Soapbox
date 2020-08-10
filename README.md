## THE CR SOAPBOX

A platform for Class Teacher to announce any changes or updates to the class schedule or any important announcements

    1.  Only The Teacher will make changes to the timetable.
    2.  Timetable is displayed in a daily schedule format.
    3.  Timetable must be avalaible round the clock and have a consistent database.
    4.  Students get notifications about changes in timetable and announcements from Teachers

To launch the bot poling mode (for developing):

    1.  Replace the text in data/bottkn.txt with bot token of CR_ALT bot
    2.  Install sqlite, json, datetime, telegram, telegram.ext, logging from pip into your system 
    3.  comment out  ~  updater.start_webhook(listen=cs.serverjson["listen"],
                        port=int(cs.serverjson["port"]),
                        url_path=bottkn,
                        key=cs.serverjson["key"],
                        cert=cs.serverjson["cert"],
                        webhook_url= url) ~
         these lines and uncomment ~ updater.start_polling() ~
         line. You can find these lines in pyFiles/CR_ALT.py file. webhook - (643-649), polling - (652)
    4.  Run this bash file in terminal : ./start.sh

If you want to launch bot in webhook mode:

    1.  You have to get ssl certificate(self-generated is also fine)
        (   To generate ssl certificate run this command : 
            openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem
            )
    2.  Replace default private.key and cert.pem files in ssl/ folder with your private.key and cert.pem files
    3.  Go to json/serverdetails.json file and fill the required details (like port, listen,FQDN)
        (   Refer this url for more details : https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks )
    4.  To Host this bot in server refer : https://github.com/python-telegram-bot/python-telegram-bot/wiki/Hosting-your-bot
