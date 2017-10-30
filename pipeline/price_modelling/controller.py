import os
from sqlalchemy import create_engine
import pandas as pd

forecast_period = 90
holdout_period = 180
response_variable = 'response'


data_dir = os.environ['DATA_DIR']
engine = create_engine(
    'sqlite:///{0}/the_reading_machine.db'.format(data_dir))


def get_igc_price(response=None):
    ''' Function to load the IGC price data.
    '''

    igc_price = pd.read_sql(
        'SELECT * FROM PriceIGC', engine, parse_dates=['date'])
    if response:
        igc_price = igc_price[['date', response]]
    return igc_price
