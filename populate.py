import keys
import pandas
import requests
import json
from datetime import datetime
import psycopg2
import psycopg2.extras
from endpoints import *
import io, csv




def populate_symbols():
    """To add any new stocks. this will check to see what symbols we already
    have and then add others taht we dont have"""

    connection = psycopg2.connect(host=keys.DB_HOST, database=keys.DB_NAME, user=keys.DB_USER, password=keys.DB_PASS)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    api = AlpacaEndpoint()
    assets = api.get_assets()



    for asset in assets:
        print(f"Inserting stock {asset.get('name')} {asset.get('symbol')}")
        cursor.execute("""
            INSERT INTO stock (name, symbol, exchange, shortable)
            VALUES (%s, %s, %s, %s)
        """, (round(asset.get('name'), 2), round(asset.get('symbol'), 2), round(asset.get('exchange'), 2), round(asset.get('shortable'), 2)))

    connection.commit()








def populate_stock_prices():


    connection = psycopg2.connect(host=keys.DB_HOST, database=keys.DB_NAME, user=keys.DB_USER, password=keys.DB_PASS)
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    symbols = []
    stock_ids = {}


    # Used the qqq.csv to get all the symbols for all the stocks in nasdaq
    with open('csv_data/qqq.csv', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            symbols.append(line[1])


    # get all stocks from database
    cursor.execute("""
        SELECT * from stock
    """)
    stocks = cursor.fetchall()


    # get all the symbols in the database and then add it the symbol and its respective id to stock_ids dict
    for stock in stocks:
        symbol = stock['symbol']
        stock_ids[symbol] = stock['id']


    ## currently have these
    #####################
    symbols = symbols[:1]
    #####################


    # slices for the alpha_vantage intraday_ext data
    slices = ['year1month1', 'year1month2', 'year1month3', 'year1month4', 'year1month5',
                'year1month6', 'year1month7', 'year1month8', 'year1month9', 'year1month10',
                'year1month11', 'year1month12', 'year2month1', 'year2month2', 'year2month3',
                'year2month4', 'year2month5', 'year2month6', 'year2month7', 'year2month8',
                'year2month9', 'year2month10', 'year2month11', 'year2month12']





    alpha = AlphaEndpoint()
    for symbol in symbols:
        print(f'Getting data for {symbol}')
        for slice in slices:
            print(f'Getting {slice}')
            data = alpha.get_data_alpha(symbol, function='intraday_ext', interval='1min', adjusted=True, outputsize='compact', datatype='csv', slice=slice).content
            temp = pd.read_csv(io.StringIO(data.decode('utf-8')), index_col='time')
            temp.index = pd.to_datetime(temp.index)

            for index, row in temp.iterrows():
                sql = """
                    INSERT INTO stock_price (stock_id, dt, open, high, low, close, volume)
                    values (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (stock_ids[symbol], str(index), row['open'], row['high'], row['low'], row['close'], row['volume']))

    connection.commit()
