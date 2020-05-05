import os
import logging
from datetime import datetime
from driver import PostgresDriver

logging.basicConfig(level=logging.DEBUG, filename='notification.log', filemode='a', format='%(asctime)s %(levelname)s:%(message)s')

if __name__ == '__main__':
    
    # start cronjob
    logging.info("Start cronjob")

    print(os.path.dirname(os.path.abspath(__file__)))

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
            logging.debug(f"Sending notification to client {client_id}")
            logging.info("Do not forget to add your food logs!")
            notified += 1
    
    logging.info(f"Notified {notified} users")
    logging.info("Finish cronjob")