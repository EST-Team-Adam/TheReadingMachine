import pickle
import controller as ctr
#from bokeh.palettes import Spectral11
#from bokeh.plotting import figure, show
from builder import TopicModel
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def summarize_array_mean(x):
    xx = x.ravel()
    return np.array([np.mean(xx[n:n + 5]) for n in range(0, len(xx), 5)])

# Load the harmonised topic sentiment data
harmonised_article = (
    ctr.harmonise_article(pos_sentiment_col='positive_sentiment',
                          neg_sentiment_col='negative_sentiment',
                          id_col='id'))

columns_to_drop = ['date', 'GOI']
input_topic_series = harmonised_article.drop(columns_to_drop, axis=1)
input_topic_series.values.sort(axis=1)

# All scores
plt.imshow(input_topic_series.values.T)
# Mean by 5, dimention from 100 to 20
#plt.imshow(np.apply_along_axis(summarize_array_mean, 1, input_topic_series.values).T)

plt.colorbar()
plt.show()
