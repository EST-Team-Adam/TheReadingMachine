import controller as ctr

target_data_table = 'MarketSentiment'
original_price_variable = 'GOI'

model_data = ctr.create_model_data()
# TODO (Michael): Add in the ability to load previous weights as
#                 prior. This will improve the stability of the
#                 construction.
weights = ctr.estimate_sentiment_weights(model_data)
market_sentiments = ctr.compute_market_sentiments(
    model_data, weights, 'date', original_price_variable)

market_sentiments.to_sql(con=ctr.engine, name=target_data_table, index=False,
                         if_exists='replace')

# Save the plot
ctr.create_sentiment_plot(market_sentiments)
