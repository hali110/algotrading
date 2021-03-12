from keys import *
import requests
import json
import datetime
import pandas as pd


class AlpacaEndpoint:
    def __init__(self):
        self.ACCT_URL = f'{BASE_URL}/v2/account'
        self.POST_ORDERS_URL = f'{BASE_URL}/v2/orders'
        self.POSITION_URL = f'{BASE_URL}/v2/positions'
        self.ASSETS_URL = f'{BASE_URL}/v2/assets'
        self.CLOCK_URL = f'{BASE_URL}/v2/clock'

        self.headers = {'APCA-API-KEY-ID': KEY_ID,
                   'APCA-API-SECRET-KEY': SECRET_KEY}




    def get_clock(self):
        """hits the alpaca clock endpoint which returns a timestamp, wether the
        market is open, the next open, and the next close"""

        r = requests.get(self.CLOCK_URL, headers=self.headers).json()
        return r



    def get_acct(self):
        """get account info, check api to see what info im getting"""

        r = requests.get(self.ACCT_URL, headers=self.headers).json()
        return r


    def get_orders(self, status='open', after=None):
        """get orders info, check api to see what info im getting

            takes two parameters
            status: open, close, or All
            after: after a certain date


        """
        if after:
            self.ORDERS_URL = f'{BASE_URL}/v2/orders?status=all&after={after}'
        else:
            self.ORDERS_URL = f'{BASE_URL}/v2/orders?status={status}'
        r = requests.get(self.ORDERS_URL, headers=self.headers).json()
        return r


    def get_pos(self):
        """get positions, check api to see what info im getting"""

        r = requests.get(self.POSITION_URL, headers=self.headers).json()
        return r


    def get_assets(self):
        """get all possisble assets, check api to see what info im getting"""

        r = requests.get(self.ASSETS_URL, headers=self.headers).json()
        return r



    def post_orders(self, sym, qty, side, type, time_in_force, limit_price=None, stop_price=None, order_class=None, take_profit=None, trail_price=None, trail_percent=None):
        """This function takes 5 parameters the
                    sym: stock symbols
                    qty: how many shares
                    side: buy or sell
                    type: market, limit, stop, stop_limit, or trailing_stop
                    time_in_force: day, gtc, opg, cls, ioc, fok
                    limit_price: in case of limit order
                    stop_price: in case of stop order
                    order_class: can be simple, bracket, oco, oto
                    take_profit: required for bracket orders



            Check alpaca docs to see what they mean. There are alot of other query
            parameters that can be used. Check them account

            this returns order info object as json


            Example Code:
                response = post_orders('AAPL', 100, 'buy', 'market', 'gtc')
                print(json.dumps(response, indent=4))


            """


        params = {
            'symbol' : sym,
            'qty' : qty,
            'side' : side,
            'type' : type,
            'time_in_force' : time_in_force,
            'order_class': order_class,
            'limit_price': limit_price,
            'take_profit': {
                "limit_price": take_profit
                },
            "stop_loss": {
                "stop_price": stop_price,
                },
            'trail_percent': trail_percent,
            'trail_price': trail_price
        }
        r = requests.post(self.POST_ORDERS_URL, json=params, headers=self.headers).json()
        return r





    def liquidate(self, sym=None, cancel_orders=True):
        """Liquidate all assets, there is also a parameter that ask if you want to
        cancel all open orders and i have this on by default """

        if(sym):
            self.LIQUIDATE_URL = f'{BASE_URL}/v2/positions/{sym}'
        else:
            self.LIQUIDATE_URL = f'{BASE_URL}/v2/positions?cancel_orders={cancel_orders}'
        r = requests.delete(self.LIQUIDATE_URL, headers=headers).json()
        return r


    def get_data(self, time, sym, start=None):
        """This gets the bar data of the symbols you want.

            Takes 3 parameters:

                    the time value (valid choices are 1Min, 5Min, 15Min and 1D)
                    symbols you want seperated by commas.
                    the start date in isoformat (example: '2019-04-15T09:30:00-04:00')
                        defualt is None

            the default number is 100 ticks but i changed it to 1000(hardcoded in the url)

            returns a json of the ticks




                    **** start is currently not working ****




            Example Code:
                data = get_data('1Min', 'AAPL,MSFT')

            """
        if(start):
            url = f'{BARS_ENDPNT}/{time}?symbols={sym}&limit=1000&start={start}'
        else:
            url = f'{BARS_ENDPNT}/{time}?symbols={sym}&limit=1000'

        r = requests.get(url, headers=headers).json()
        return r







    def make_df(self, data):
        """Takes in the json that you get from get_data function and puts them into
        a dict of dataframes"""
        d = {}
        for symbol in data.keys():
             times = [datetime.datetime.fromtimestamp(i.pop('t')) for i in data[symbol]]
             cols = list(data[symbol][0].keys())
             d[symbol] = pd.DataFrame(index=times, columns=cols, data=data[symbol])

        return d







    def last_quote(self, sym):
        """This provides the last quote details for a symbol"""

        url = f'https://data.alpaca.markets/v1/last_quote/stocks/{sym}'

        r = requests.get(url, headers=headers).json()
        return r






    def last_trade(self, sym):
        """This provides the last trade details for a symbol"""

        url = f'https://data.alpaca.markets/v1/last/stocks/{sym}'

        r = requests.get(url, headers=headers).json()
        return r



    # to output to file
    #if __name__ == '__main__':
    #    print(json.dumps(get_data('1Min', 'TSLA'), indent=4))








class AlphaEndpoint:
    def get_data_alpha(self, sym, function='intraday', interval='1min', adjusted=True, outputsize='compact', datatype='json', slice=None, write=None):
        """This function is to get data from the alphavantage api. It takes 8 parameters:

                function: REQUIRED - this is to say wether you want 'intraday', 'daily',
                    'daily_adj', 'intraday_ext', 'weekly', weekly_adj, 'monthly',
                    'monthly_adj', 'quote', 'fundamentals', 'income', 'balance', 'cash'
                sym: REQUIRED - the symbol you want data for
                interval: REQUIRED if choose intraday - default is '1min' but can have '1min', '5min', '15min', '30min', '60min'
                adjusted: default is true. This will adjust the output data by historical split and dividend events
                    set False to get raw(as-traded values)
                outputsize: default is 'compact', can also have 'full'. compact gives the 100 latest data points and full will the full-length intraday time series
                datatype: default is 'json' but can also have 'csv' in which case a csv file is returned
                slice: REQUIRED if using intraday_ext - Their docs say:
                    "Two years of minute-level intraday data contains over 2 million data points, which can take up to Gigabytes of memory.
                    To ensure optimal API response speed, the trailing 2 years of intraday data is evenly divided into 24 "slices" -
                    year1month1, year1month2, year1month3, ..., year1month11, year1month12, year2month1, year2month2, year2month3, ..., year2month11, year2month12.
                    Each slice is a 30-day window, with year1month1 being the most recent and year2month12 being the farthest from today. By default, slice=year1month1."
                write: if true, this will write the data to a csv in teh same directory, otherwise it will
                    attempt to put it in json. If false, it will do neither. Default is none so json

            this will return a json unless csv is selected. If so, it will save a csv file

            This can also return a bunch of technical indicators. If u want that: go look at the docs

            their docs: 'https://www.alphavantage.co/documentation/'

        """






        url = 'https://www.alphavantage.co/query'
        if(function == 'intraday'):
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol':sym,
                'interval': interval,
                'adjusted': adjusted,
                'outputsize': outputsize,
                'datatype': datatype,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'intraday_ext'):
            params = {
                'function': 'TIME_SERIES_INTRADAY_EXTENDED',
                'symbol': sym,
                'slice': slice,
                'interval': interval,
                'adjusted': adjusted,
                'datatype': 'csv',
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'daily'):
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol':sym,
                'outputsize': outputsize,
                'datatype': datatype,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'daily_adj'):
            params = {
                'function': 'TIME_SERIES_DAILY_ADJUSTED',
                'symbol':sym,
                'outputsize': outputsize,
                'datatype': datatype,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'weekly'):
            params = {
                'function': 'TIME_SERIES_WEEKLY',
                'symbol':sym,
                'datatype': datatype,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'weekly_adj'):
            params = {
                'function': 'TIME_SERIES_WEEKLY_ADJUSTED',
                'symbol':sym,
                'datatype': datatype,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'monthly'):
            params = {
                'function': 'TIME_SERIES_MONTHLY',
                'symbol':sym,
                'datatype': datatype,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'monthly_adj'):
            params = {
                'function': 'TIME_SERIES_MONTHLY_ADJUSTED',
                'symbol':sym,
                'datatype': datatype,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'quote'):
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol':sym,
                'datatype': datatype,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'fundamentals'):
            params = {
                'function': 'OVERVIEW',
                'symbol':sym,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'income'):
            params = {
                'function': 'INCOME_STATEMENT',
                'symbol':sym,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'balance'):
            params = {
                'function': 'BALANCE_STATEMENT',
                'symbol':sym,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)
        elif(function == 'cash'):
            params = {
                'function': 'CASH_FLOW',
                'symbol':sym,
                'apikey': ALPHA_VANTAGE_KEY}
            r = requests.get(url=url, params=params)














        if(write == True):
            name = sym + '.csv'
            path = '/csv_data/' + name
            with open(path, 'w') as f:
                f.write(r.text)
        elif(write == False):
            r = r.json()


        return r






    def make_df_alpha(self, data):
        """Takes in json and will make it into a df"""
        data = data.json()
        temp = [item for item in data.keys()]
        data = data[temp[1]]

        df = pd.DataFrame.from_dict(data, orient='index')
        cols = [item[3:] for item in df.columns]

        df.columns = cols

        return df
