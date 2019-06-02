from crontab import CronTab

cron = CronTab(user='damian')  
job = cron.new(command='python3 /home/damian/projects/ovdataload/petl/crontest.py', comment='my comment')  
job.minute.every(1)

print(job)

cron.write() 

