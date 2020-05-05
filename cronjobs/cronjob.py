import os
from crontab import CronTab

username = os.getenv('USER')

cron = CronTab(user=username)

job = cron.new(command=f'python3 /home/{username}/Documents/rest-api/cronjobs/text.py', comment="dateInfo")

job.hour.on(18)
job.minute.on(30)

for job in cron:
    print(cron)

cron.write()
