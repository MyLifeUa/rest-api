import os
from crontab import CronTab

# get crontab
cron = CronTab(user=username)

for job in cron:
    print(cron)

job = cron.new(command=f'python3 {os.path.dirname(os.path.abspath(__file__))}/notification.py', comment="afternoon_notification")
job2 = cron.new(command=f'python3 {os.path.dirname(os.path.abspath(__file__))}/notification.py', comment="night_notification")

# afternoon notification at 15:01
job.hour.on(15)
job.minute.on(1)

# night notification at 21:01
job.hour.on(21)
job.minute.on(1)

# save changes to crontab
#cron.write() 
