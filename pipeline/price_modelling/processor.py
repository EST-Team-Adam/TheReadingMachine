import os
import controller as ctr
from sqlalchemy import create_engine

# Configuration
data_dir = os.environ['DATA_DIR']
target_data_table = 'PriceForecast'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))

# Model parameters
forecast_period = 180
holdout_period = 2

response_variable = 'response'
filter_coef = 1
alpha = 1
bootstrapIteration = 50

# Data extraction and processing
topic_variables = ctr.get_topic_variables()
price_data = ctr.get_igc_price(response='GOI')
harmonised_data = ctr.get_harmonised_data()
transformed_data = (
    ctr.transform_harmonised_data(data=harmonised_data,
                                  forecast_period=forecast_period,
                                  topic_variables=topic_variables,
                                  filter_coef=filter_coef,
                                  response_variable=response_variable))

# Model fitting
smoothed_prediction = (
    ctr.train_bag_elasticnet(complete_data=transformed_data,
                             forecast_period=forecast_period,
                             holdout_period=holdout_period,
                             bootstrapIteration=bootstrapIteration,
                             topic_variables=topic_variables,
                             response_variable=response_variable))


# Save the prediction back to the DB
smoothed_prediction.to_sql(con=engine, name=target_data_table, index=False,
                           if_exists='replace')
