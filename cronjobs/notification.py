import os
import json
import logging
import requests
from datetime import datetime
from driver import PostgresDriver

logging.basicConfig(level=logging.DEBUG, filename=f'{os.path.dirname(os.path.abspath(__file__))}/notification.log', filemode='a', format='%(asctime)s %(levelname)s:%(message)s')

EXPO_URL = 'https://exp.host/--/api/v2/push/send'
EXPO_HEADERS = {
    'Host': 'exp.host',
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/json'
}


if __name__ == '__main__':
    
    # start cronjob
    logging.info("Start cronjob")

    # today date
    today = datetime.today().strftime("%Y-%m-%d")
    logging.debug(f"Today date: {today}")

    # database connection
    dolphin = PostgresDriver()
    logging.info(f"Database connected with success on {dolphin.host}:{dolphin.port}!")

    # get all clients from database
    logging.debug("\nSELECT * FROM rest_api_client;")
    clients = sorted(dolphin.select_all("SELECT * FROM rest_api_client;"))
    logging.debug(f"Query result: \n{clients}")

    
    notified = 0    # counter of notified users
    for client in clients:
        client_id = int(client[0])

        # get all meals of each client
        logging.debug(f"\nSELECT * FROM rest_api_mealhistory WHERE client={client_id};")
        meals = dolphin.select_all(f"SELECT * FROM rest_api_mealhistory WHERE rest_api_mealhistory.client_id={client_id} AND rest_api_mealhistory.day='{today}';")
        logging.debug(f"Query result: \n{meals}")

        # if there are no meals, send notification to client
        if not meals:
            tokens = dolphin.select_all(f"SELECT * FROM rest_api_expotoken WHERE rest_api_expotoken.client_id={client_id};")
            
            for token in tokens:
                logging.info(f"Sending notification to client {client_id}, device {token[1]}")
                

                payload = {
                    'to': token[1],
                    'title': 'MyLife reminder',
                    'body': 'Do not forget to add your food logs!'
                }

                try:
                    response = requests.post(url=EXPO_URL, data=json.dumps(payload), headers=EXPO_HEADERS)
                    logging.info(f"User notified with success! Response: {response}")
                except:
                    pass

            notified += 1
    
    logging.info(f"Notified {notified} users")
    logging.info("Finish cronjob")
