from datetime import datetime


with open('/home/tiagocm/Documents/rest-api/cronjobs/dateInfo.txt', 'a') as outFile:
    outFile.write("\nAccessed on " + str(datetime.now()))