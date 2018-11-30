import os
import pandas as pd
import sqlalchemy
import datetime

# Configuration
data_dir = os.environ['DATA_DIR']
data_target_table = 'PriceIGC'
engine = sqlalchemy.create_engine(
    'sqlite:///{0}/the_reading_machine.db'.format(data_dir))

price = pd.read_csv('igc_goi.csv').rename(columns={'IGC GOI': 'GOI'})
price['date'] = [datetime.datetime.strptime(
    d, '%m/%d/%Y').date() for d in price['DATE']]
price = price.drop('DATE', 1)


field_type = {'date': sqlalchemy.types.Date(),
              'GOI': sqlalchemy.types.Integer(),
              'Wheat': sqlalchemy.types.Integer(),
              'Maize': sqlalchemy.types.Integer(),
              'Rice': sqlalchemy.types.Integer(),
              'Barley': sqlalchemy.types.Integer(),
              'Soyabeans': sqlalchemy.types.Integer()
              }

price.to_sql(con=engine, name=data_target_table, if_exists='replace',
             index=False, dtype=field_type)
