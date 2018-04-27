import pandas as pd
import thereadingmachine.modeller.bagged_elasticnet as mbe
import thereadingmachine.modeller.lstm_k_step as mlks
import thereadingmachine.environment as env

# Model the price
elasticnet_prediction = mbe.output()
lstm_prediction = mlks.output()
all_prediction = pd.concat([elasticnet_prediction, lstm_prediction])


# Save the prediction back to the DB
all_prediction.to_sql(con=env.engine, name=env.price_table, index=False,
                      if_exists='replace')
