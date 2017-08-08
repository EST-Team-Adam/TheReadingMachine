import os
import sqlalchemy
from sqlalchemy import create_engine
import controller as ctr


# Configuration
data_dir = os.environ['DATA_DIR']
data_target_table = 'PriceIGC'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))

goi_script = ctr.extract_goi_page()
price_data = ctr.parse_goi_script(goi_script)


field_type = {'date': sqlalchemy.types.Date(),
              'GOI': sqlalchemy.types.Integer(),
              'Wheat': sqlalchemy.types.Integer(),
              'Maize': sqlalchemy.types.Integer(),
              'Rice': sqlalchemy.types.Integer(),
              'Barley': sqlalchemy.types.Integer(),
              'Soyabeans': sqlalchemy.types.Integer()
              }

price_data.to_sql(con=engine, name=data_target_table,
                  if_exists='replace',
                  index=False, dtype=field_type)
