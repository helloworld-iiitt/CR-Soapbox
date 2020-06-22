import datetime
from pytz import timezone
fmt = '%H:%M:%S %Z %z'
utc_dt = datetime.time(hour = 18,minute = 8,tzinfo = timezone('Asia/Kolkata'))
print(datetime.datetime.now(tz = timezone('Asia/Kolkata')).strftime(fmt))
print(utc_dt.strftime(fmt))