import configparser  # 1
import oandapyV20 as opy  # 2
from oandapyV20 import API
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
import pandas as pd  # 6
import numpy as np  # 11
import seaborn as sns; sns.set()  # 18
import json


config = configparser.ConfigParser()
config.read('oanda.cfg')

oanda = opy.API(environment='practice', access_token=config['oanda']['access_token'])

def setups():
    # data = oanda.get_history(instrument='EUR_USD',  # our instrument
    #                          start='2016-12-08',  # start data
    #                          end='2016-12-10',  # end date
    #                          granularity='M1')  # minute bars
    instrument = 'EUR_USD'
    params = {
      "granularity": "M1",
      "from": "2016-12-08T12:00:00Z",
      "to": "2016-12-10T12:00:00Z"
    }

    data = json.dumps(opy.contrib.factories.InstrumentsCandlesFactory(instrument = instrument, params = params))

    df = pd.DataFrame(data['candles']).set_index('time')

    df.index = pd.DatetimeIndex(df.index)

    df.info()

def momentum():
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
