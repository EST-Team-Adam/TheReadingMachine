import os
import pandas as pd
import modeler_bagged_elasticnet as mbe
import modeler_lstm_k_step as mlks
from sqlalchemy import create_engine

# Configuration
data_dir = os.environ['DATA_DIR']
target_data_table = 'PriceForecast'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))

elasticnet_prediction = mbe.output()
lstm_prediction = mlks.output()
all_prediction = pd.concat([elasticnet_prediction, lstm_prediction])


# Save the prediction back to the DB
all_prediction.to_sql(con=engine, name=target_data_table, index=False,
                      if_exists='replace')
