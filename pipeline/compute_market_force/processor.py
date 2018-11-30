import pandas as pd
import thereadingmachine.environment as env
import thereadingmachine.modeller.compute_market_force as ctr
import thereadingmachine.parameter as param
import thereadingmachine.utils.io as io

market_sentiments = list()
market_sentiments_index = list()
for price in param.price_variables:
    model_data = ctr.create_model_data(price, param.price_variables)
    # TODO (Michael): Add in the ability to load previous weights as
    #                 prior. This will improve the stability of the
    #                 construction.
    weights = ctr.estimate_sentiment_weights(model_data, price)
    individual_price_sentiments = ctr.compute_market_sentiments(
        model_data, weights, 'date', price)
    sentiment_index = ctr.compute_sentiment_index(individual_price_sentiments)
    market_sentiments.append(individual_price_sentiments)
    market_sentiments_index.append(sentiment_index)
    ctr.create_sentiment_plot(individual_price_sentiments, price)


# Concatenate the list for saving and plotting
market_sentiments_df = pd.concat(market_sentiments)
market_sentiments_index_df = pd.concat(market_sentiments_index)

# Plot the traffic light
ctr.create_sentiment_traffic_light(market_sentiments_index_df)

# Save the sentiments back
io.save_table(data=market_sentiments_df, table_name=env.market_force_table)
