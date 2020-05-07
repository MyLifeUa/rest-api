import os
from crontab import CronTab

username = os.getenv('USER')

# get crontab
cron = CronTab(user=username)

# remove old notifications cronjobs
cron.remove_all(comment='afternoon_notification')
cron.remove_all(comment='night_notification')

# create new cronjobs
job = cron.new(command=f'docker exec compose_django_1 python3 /code/cronjobs/notification.py', comment="afternoon_notification")
job2 = cron.new(command=f'docker exec compose_django_1 python3 /code/cronjobs/notification.py', comment="night_notification")

# afternoon notification at 15:01
job.hour.on(14)
job.minute.on(1)

# night notification at 21:01
job2.hour.on(20)
job2.minute.on(1)

# save changes to crontab
cron.write()
