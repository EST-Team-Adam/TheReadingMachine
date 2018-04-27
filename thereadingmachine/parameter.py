import colorlover as cl
from datetime import datetime

########################################################################
# Article Processing
########################################################################

# Manual invalid title and link
maintenance_title = ['Reduced service at Agrimoney.com',
                     'Apology to Agrimoney.com subscribers']

irrelevant_link = ['https://www.euractiv.com/topics/news/?type_filter=video',
                   'http://www.euractiv.com/topics/news/?type_filter=video',
                   'http://www.euractiv.com/topics/news/?type_filter=news',
                   'http://www.euractiv.com/topics/news/?type_filter=all',
                   'https://www.euractiv.com/topics/news/?type_filter=all',
                   'https://www.euractiv.com/topics/news/',
                   'https://www.euractiv.com/topics/news/?type_filter=news',
                   'http://www.euractiv.com/topics/news/',
                   'https://www.euractiv.com/news/',
                   'http://www.euractiv.com/news/']

# Initialise processing parameters
min_length = 30
remove_captalisation = True
remove_noun = True
remove_numerical = True
remove_punctuation = True
stem = False


########################################################################
# Sentiment model
########################################################################

# Target variables
price_variables = ['Wheat', 'Maize', 'Soyabean', 'Rice']
response_variable = 'response'

# Model
model_start_date = datetime(2010, 1, 1).date()

# Model parameters
filter_coef = 1
sentiment_scale = 50
bootstrapIteration = 75
forecast_period = 0
holdout_period = 180

# RNN Model parameters
feature_size = 100
timestep_size = 90
batch_size = 90
num_layer = 2
cell_size = 128
learning_rate = 0.0001
epochs = 300
keep_prob = 0.75
clipping_cap = 1.0


########################################################################
# Plotting and dashboard
########################################################################

# Plot parameters
div_col_pallete = [cl.scales['11']['div']['RdYlGn'][i]
                   for i in [10, 8, 5, 2, 0]]
price_color = 'rgb(91, 146, 229)'
