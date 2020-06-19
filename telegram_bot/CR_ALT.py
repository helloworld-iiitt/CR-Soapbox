import threading
from python.dbCreate import teleDb
from python.pystdcb import stdchat
from python.pytchcb import tchchat

lock = threading.Lock

db = teleDb()
stdcht = stdchat(db)
tchcht = tchchat(db)
stdcht.updater.start_polling()
print("Getting Updates of CR_ALT")
tchcht.updater.start_polling()
print("Getting Updates of CR_ALT(TCH)")
stdcht.updater.idle()
tchcht.updater.idle()