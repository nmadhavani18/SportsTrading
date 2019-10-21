import configparser  # 1
import oandapyV20 as opy  # 2
from oandapyV20 import API
from oandapyV20.contrib.factories import InstrumentsCandlesFactory
import pandas as pd  # 6
import numpy as np  # 11
import seaborn as sns; sns.set()  # 18
import json
import oandapyV20.endpoints.instruments as instruments


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
    df = list()

    data = instruments.InstrumentsCandles(instrument = instrument, params = params)

    oanda.request(data)

    df.append(data.response)
    print(df)

    df.index = pd.DatetimeIndex(df.index)

    df.info()

# def DataFrameFactory(r, colmap=None, conv=None):
#     def convrec(r, m):
#         """convrec - convert OANDA candle record.
#
#         return array of values, dynamically constructed, corresponding with config in mapping m.
#         """
#         v = []
#         for keys in [x.split(":") for x in m.keys()]:
#             _v = r.get(keys[0])
#             for k in keys[1:]:
#                 _v = _v.get(k)
#             v.append(_v)
#
#         return v
#
#     record_converter = convrec if conv is None else conv
#     column_map_ohlcv = OrderedDict([
#        ('time', 'D'),
#        ('mid:o', 'O'),
#        ('mid:h', 'H'),
#        ('mid:l', 'L'),
#        ('mid:c', 'C'),
#        ('volume', 'V')
#     ])
#     cmap = column_map_ohlcv if colmap is None else colmap
#
#     df = pd.DataFrame([list(record_converter(rec, cmap)) for rec in r.get('candles')])
#     df.columns = list(cmap.values())
#     #df.rename(columns=colmap, inplace=True)  # no need to use rename, cmap values are ordered
#     df.set_index(pd.DatetimeIndex(df['D']), inplace=True)
#     del df['D']
#     df = df.apply(pd.to_numeric)  # OANDA returns string values: make all numeric
#     return df

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
