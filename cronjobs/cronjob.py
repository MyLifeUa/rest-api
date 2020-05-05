
if __name__ == '__main__':
    dolphin = PostgresDriver()

    clients = dolphin.select_all("SELECT * FROM Client")

    print(clients)