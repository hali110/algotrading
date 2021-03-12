import keys
import pandas
import requests
import json
from datetime import datetime
import psycopg2
import psycopg2.extras
from endpoints import AlpacaEndpoint




def populate_symbols():
    """To add any new stocks. this will check to see what symbols we already
    have and then add others taht we dont have"""


    connection = psycopg2.connect(host=keys.DB_HOST, database=keys.DB_NAME, user=keys.DB_USER, password=keys.DB_PASS)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
        SELECT * FROM stock
        """)

    ## giving a list
    rows = cursor.fetchall()
    symbols = [row['symbol'] for row in rows]

    alp = AlpacaEndpoint()
    assets = alp.get_assets()

    for asset in assets:
        try:
            if asset['status'] == 'active' and asset['tradable'] and asset['symbol'] not in symbols:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                print(f"{now} : Added a new stock {asset['symbol']} - {asset['name']}")
                cursor.execute("INSERT INTO stock (symbol, name, exchange) VALUES (%, %, %)", (asset['symbol'], asset['name'], asset['exchange']))
        except Exception as e:
            print(asset['symbol'])
            print(e)

    connection.commit()
