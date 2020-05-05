import logging
from datetime import datetime
from driver import PostgresDriver

logging.basicConfig(level=logging.DEBUG, filename='cronjob.log', filemode='w', format='%(asctime)s %(levelname)s:%(message)s')

if __name__ == '__main__':

    # start cronjob
    logging.info("Start cronjob")

    # today date
    today = datetime.today().strftime("%Y-%m-%d")
    logging.debug(f"Today date: {today}")

    # database connection
    dolphin = PostgresDriver()
    logging.info(f"Database connected with success on {dolphin.host}:{dolphin.port}!")

    logging.debug("SELECT * FROM rest_api_client;")
    clients = sorted(dolphin.select_all("SELECT * FROM rest_api_client;"))
    logging.debug(f"Query result: \n{clients}")

    for client in clients:
        client_id = int(client[0])
        logging.debug(f"SELECT * FROM rest_api_mealhistory WHERE client={client_id};")
        meals = dolphin.select_all(f"SELECT * FROM rest_api_mealhistory WHERE rest_api_mealhistory.client_id={client_id} AND rest_api_mealhistory.day='{today}';")
        logging.debug(f"Query result: \n{meals}")