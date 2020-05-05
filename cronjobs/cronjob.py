import os
from crontab import CronTab

username = os.getenv('USER')

# get crontab
cron = CronTab(user=username)

# remove old notifications cronjobs
cron.remove_all(comment='afternoon_notification')
cron.remove_all(comment='night_notification')

# create new cronjobs
job = cron.new(command=f'python3 {os.path.dirname(os.path.abspath(__file__))}/notification.py', comment="afternoon_notification")
job2 = cron.new(command=f'python3 {os.path.dirname(os.path.abspath(__file__))}/notification.py', comment="night_notification")

# afternoon notification at 15:01
job.hour.on(22)
job.minute.on(5)

# night notification at 21:01
job2.hour.on(22)
job2.minute.on(10)

for job in cron:
    print(cron)

# save changes to crontab
cron.write()
