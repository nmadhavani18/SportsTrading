import configparser
import oandapyV20 as opy
from oandapyV20 import API
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
import pandas as pd
import numpy as np
import seaborn as sns; sns.set()
import json
import oandapyV20.endpoints.instruments as instruments
from pprint import pprint

config = configparser.ConfigParser()
config.read('oanda.cfg')

oanda = opy.API(environment='practice', access_token=config['oanda']['access_token'])

def setups():
    instrument = 'EUR_USD'
    params = {
      "granularity": "M1",
      "from": "2016-12-08T12:00:00Z",
      "to": "2016-12-10T12:00:00Z"
    }
    convertedDF = list()

    data = instruments.InstrumentsCandles(instrument = instrument, params = params)

    oanda.request(data)
    for key in data.response.keys():
        convertedDF.append(data.response.get(key))

    # pprint(pd.DataFrame(convertedDF[2]).set_index('time'))

    df = pd.DataFrame(convertedDF[2]).set_index('time')
    df.index = pd.DatetimeIndex(df.index)
    df.groupby(pd.Grouper(freq='1H')).agg(['first', 'last', 'max'])

    fs = dict(Open='first', Close='last', Max='max')
    ag = dict(Ask=fs, Bid=fs)
    gp = pd.Grouper(freq='1H')
    d1 = df.rename(columns=str.capitalize).groupby(gp).agg(ag)
    d1.sort_index(axis=1, ascending=False, inplace=True)
    d1.columns = d1.columns.map('{0[1]} {0[0]}'.format)
    print(d1)

    # pprint(df)

    df.info()

    # momentum algorithmic function

    df['returns'] = np.log(df['closeAsk'] / df['closeAsk'].shift(1))  # 12

    cols = []  # 13

    for momentum in [15, 30, 60, 120]:  # 14
        col = 'position_%s' % momentum  # 15
        df[col] = np.sign(df['returns'].rolling(momentum).mean())  # 16
        cols.append(col)  # 17


def show_graph():
    from IPython import get_ipython
    get_ipython().run_line_magic('matplotlib', 'inline')
    strats = ['returns']

    for col in cols:
        strat = 'strategy_%s' % col.split('_')[1]
        df[strat] = df[col].shift(1) * df['returns']
        strats.append(strat)

    df[strats].dropna().cumsum().apply(np.exp).plot()

setups()
momentum()
show_graph()
