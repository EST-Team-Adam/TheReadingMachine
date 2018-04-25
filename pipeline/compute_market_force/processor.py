import pandas as pd
import controller as ctr

target_data_table = 'MarketForce'
price_variables = ['Wheat', 'Maize', 'Soyabean', 'Rice']

market_sentiments = list()
market_sentiments_index = list()
for price in price_variables:
    model_data = ctr.create_model_data(price, price_variables)
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
market_sentiments_df.to_sql(con=ctr.engine, name=target_data_table,
                            index=False, if_exists='replace')
