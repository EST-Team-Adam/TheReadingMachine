import os
import io
import pandas as pd
import numpy as np
import tensorflow as tf
from datetime import datetime
from datetime import timedelta
from sklearn import preprocessing
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
import thereadingmachine.parameter as param
import thereadingmachine.environment as env
from thereadingmachine.utils.io import read_table


# This is because the model needs timestep and forecast period ahead
# data to make the first forecast.
rnn_start_date = param.model_start_date - \
    timedelta(days=param.timestep_size + param.forecast_period)


def get_topic_modelled_article():
    topic_modelled_article = read_table(env.topic_model_table, dates=False)
    sclae_input = topic_modelled_article.drop('id', axis=1)
    scaled_topic = pd.DataFrame(preprocessing.scale(sclae_input),
                                columns=sclae_input.columns)
    scaled_topic['id'] = topic_modelled_article['id']
    return scaled_topic


def compute_topic_score(pos_sentiment_col, neg_sentiment_col, topic,
                        id_col='id'):
    original_id = topic[id_col]
    compound_sentiment = preprocessing.scale(
        pos_sentiment_col - neg_sentiment_col)
    scored_topic = topic.drop(id_col, axis=1).apply(
        lambda x: x * compound_sentiment)

    scored_topic[id_col] = original_id
    return scored_topic


def harmonise_article(pos_sentiment_col='positive_sentiment',
                      neg_sentiment_col='negative_sentiment',
                      id_col='id', date_col='date'):
    '''The function harmonised the various data sources and return a
    hamonised dataset for modeling.

    '''
    sentiment_scored_article = read_table(env.sentiment_scored_table)
    topic_modelled_article = get_topic_modelled_article()
    igc_price = read_table(env.price_table)

    article_max_date = sentiment_scored_article[date_col].max()
    model_price = igc_price[(igc_price[date_col] >= rnn_start_date) &
                            (igc_price[date_col] <= article_max_date)]

    scored_topic = compute_topic_score(
        pos_sentiment_col=sentiment_scored_article[pos_sentiment_col],
        neg_sentiment_col=sentiment_scored_article[neg_sentiment_col],
        topic=topic_modelled_article, id_col=id_col)
    scored_topic[date_col] = sentiment_scored_article[date_col]

    # Perform aggregation
    aggregated_article = (scored_topic
                          .drop('id', axis=1)
                          .groupby(date_col)
                          .mean()
                          .apply(lambda x: x / x.abs().max(), axis=0)
                          )
    aggregated_article[date_col] = aggregated_article.index

    # NOTE (Michael): dates without sentiments and topic are filled
    #                 with 0 assuming there are no information
    #                 available.
    harmonised_data = (pd.merge(model_price, aggregated_article,
                                on=date_col, how='left')
                       .fillna(0))

    return harmonised_data


def data_preprocess(data, feature_size, forecast_period):
    '''Function to process the data.

    The target is shifted and then scaled, the data is subsetted
    depending on the feature size.

    A denormaliser is also returned to rescale the prediction back to
    the original scale

    '''
    no_date_data = data.drop('date', axis=1)
    no_date_data['current_price'] = no_date_data['GOI'][:]
    no_date_data['GOI'] = no_date_data['GOI'].shift(-forecast_period)
    price_mean = no_date_data['GOI'].mean()
    price_sd = no_date_data['GOI'].std()
    no_date_data['GOI'] = (no_date_data['GOI'] - price_mean) / price_sd
    no_date_data = no_date_data.iloc[:, :feature_size + 1]

    def forecast_denormaliser(forecast):
        return pd.Series(forecast) * price_sd + price_mean
    return no_date_data, forecast_denormaliser


class SentimentRnn:
    '''A sentiment RNN model takes the topic sentiment score to predict
    the target commodity price.

    The data need to contain the features (topic sentiment score) and
    also the target (commodity price). Then target column name should
    be specified.

    '''

    def __init__(self, data, response_col, denormaliser,
                 forecast_period, feature_size, timestep_size, batch_size,
                 num_layer, cell_size, learning_rate, holdout_period, epochs,
                 keep_prob, clipping_cap, log_dir, model_name=None):

        self.data = data.copy()
        self.response_col = response_col
        self.denormaliser = denormaliser
        self.forecast_period = forecast_period
        self.feature_size = feature_size
        self.timestep_size = timestep_size
        self.batch_size = batch_size
        self.num_layer = num_layer
        self.cell_size = cell_size
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.keep_prob = keep_prob
        self.clipping_cap = clipping_cap
        self.holdout_period = holdout_period
        self.log_dir = log_dir

        # Build the graph
        self.build_graph()

        if model_name is None:
            # HACK (Michael): This assumes that we have 100 features
            self.log_string = 'lr={},ls={},cs={},kp={}'.format(
                self.learning_rate, self.num_layer, self.cell_size,
                self.keep_prob)
        else:
            self.log_string = model_name

        # Create the train, valid and prediction data sets.
        self.train_data, self.valid_data, self.pred_data = self.split_data()

    def split_data(self):
        '''Split the data into training, test and prediction set.

        '''
        prediction_set = self.data[self.data[self.response_col].isnull()]
        working_set = self.data[self.data[self.response_col].notnull()]
        training_set = working_set[:-self.holdout_period]
        valid_set = working_set[-self.holdout_period:]
        return training_set, valid_set, prediction_set

    def create_sample_generator(self, input_data, batch_size):
        '''The function creates a generator which will split and the return
        the batch data.

        '''
        target_serie = np.array(input_data[self.response_col])
        inputs_matrix = np.array(input_data.drop(self.response_col, axis=1))
        series_length = len(target_serie)
        num_slide = series_length - self.timestep_size + 1
        truncated_num_slide = (num_slide / batch_size) * batch_size
        num_batch = truncated_num_slide / batch_size

        input_list = [None] * truncated_num_slide
        target_list = [None] * truncated_num_slide
        for slide in range(truncated_num_slide):
            slide_end = slide + self.timestep_size
            input_list[slide] = np.array(inputs_matrix[slide:slide_end, :])
            target_list[slide] = target_serie[slide_end - 1]

        batch_input = np.split(np.stack(input_list), num_batch)
        batch_target = np.split(
            np.stack(target_list).reshape(-1, 1), num_batch)
        for i in range(num_batch):
            yield batch_input[i], batch_target[i]

    def build_graph(self):
        ''' Initialise the graph for training.
        '''
        # Reset all previous graph
        tf.reset_default_graph()
        self.graph = tf.Graph()
        with tf.Session(graph=self.graph) as sess:
            with tf.name_scope('inputs'):
                self.input_ = tf.placeholder(
                    tf.float32,
                    shape=[None, self.timestep_size, self.feature_size],
                    name='input')
                self.target_ = tf.placeholder(
                    tf.float32, shape=[None, 1], name='target')
                self.batch_size_ = tf.placeholder(
                    tf.int32, shape=(), name='batch_size')
                self.is_training = tf.placeholder(tf.bool, name='is_training')

            with tf.name_scope('process'):
                # Reverse the input
                reversed_input = tf.reverse(
                    self.input_, [-1], name='reverse_input')

            with tf.name_scope('rnn'):
                # Create the lstm
                lstm = tf.contrib.rnn.MultiRNNCell(
                    cells=[
                        tf.contrib.rnn.BasicLSTMCell(
                            num_units=self.cell_size)
                        for _ in range(self.num_layer)])

                self.initial_state = lstm.zero_state(
                    batch_size=self.batch_size_, dtype=tf.float32)

                output, self.final_state = tf.nn.dynamic_rnn(cell=lstm,
                                                             inputs=reversed_input,
                                                             initial_state=self.initial_state)

            with tf.name_scope('fnn'):
                # Fully connected layers
                flattened = output[:, -1]
                fc1 = tf.contrib.layers.fully_connected(inputs=flattened,
                                                        num_outputs=int(
                                                            self.cell_size / 2),
                                                        activation_fn=None)
                fc1 = tf.nn.dropout(
                    fc1, keep_prob=self.keep_prob, name='fc1_drop')
                # fc1 = tf.layers.batch_normalization(fc1,
                #                                     training=self.is_training)
                fc1 = tf.nn.relu(fc1)
                self.prediction = tf.contrib.layers.fully_connected(inputs=fc1,
                                                                    num_outputs=1,
                                                                    activation_fn=None)
                # TODO (Michael): Normalise the prediction
                tf.summary.histogram('predictions', self.prediction)

            with tf.name_scope('optimisation'):
                # Calculate the loss
                self.loss = tf.losses.mean_squared_error(labels=self.target_,
                                                         predictions=self.prediction)
                tf.summary.scalar('loss', self.loss)

                # # Training operation
                # with
                # tf.control_dependencies(tf.get_collection(tf.GraphKeys.UPDATE_OPS)):
                optimiser = tf.train.AdamOptimizer(
                    learning_rate=self.learning_rate)
                gradients, variables = zip(
                    *optimiser.compute_gradients(self.loss))
                gradients, _ = tf.clip_by_global_norm(gradients,
                                                      self.clipping_cap)
                self.train_op = optimiser.apply_gradients(
                    zip(gradients, variables))

            self.merged = tf.summary.merge_all()

    def train(self):
        '''The training method, this will train the model and also write the
        summary for Tensorboard.

        '''
        print('Training model: {}'.format(self.log_string))
        with tf.Session(graph=self.graph) as sess:
            train_writer = tf.summary.FileWriter(
                self.log_dir + '/train/' + self.log_string)
            test_writer = tf.summary.FileWriter(
                self.log_dir + '/valid/' + self.log_string)
            self.saver = tf.train.Saver()
            sess.run(tf.global_variables_initializer())

            for e in range(self.epochs):
                train_generator = self.create_sample_generator(
                    input_data=self.train_data, batch_size=self.batch_size)

                train_state = sess.run(self.initial_state,
                                       feed_dict={self.batch_size_: self.batch_size})

                for train_batch, (train_input, train_target) in enumerate(train_generator):
                    train_loss, _, train_summary, train_state = sess.run(
                        [self.loss, self.train_op,
                         self.merged, self.final_state],
                        feed_dict={self.input_: train_input,
                                   self.target_: train_target,
                                   self.batch_size_: self.batch_size,
                                   self.initial_state: train_state,
                                   self.is_training: True})

                train_writer.add_summary(train_summary, e)

                valid_generator = self.create_sample_generator(
                    input_data=self.valid_data, batch_size=self.batch_size)
                valid_state = train_state
                for valid_batch, (valid_input, valid_target) in enumerate(valid_generator):
                    valid_loss, valid_state, test_summary = sess.run(
                        [self.loss, self.final_state, self.merged],
                        feed_dict={self.input_: valid_input,
                                   self.target_: valid_target,
                                   self.batch_size_: self.batch_size,
                                   self.initial_state: valid_state,
                                   self.is_training: False})
                test_writer.add_summary(test_summary, e)

                print('Epoch: {}/{} -- Train loss: {:.5f} -- Valid loss: {:.5f}'.format(
                    e + 1, self.epochs, train_loss, valid_loss))
            self.saver.save(
                sess, '{}/checkpoints/model.ckpt'.format(self.log_dir))

    def predict(self):
        '''Method to generate the complete prediction, this includes the fit.

        '''
        with tf.Session(graph=self.graph) as sess:
            self.saver.restore(
                sess, tf.train.latest_checkpoint('{}/checkpoints'.format(self.log_dir)))
            forecast = []
            forecast_generator = self.create_sample_generator(
                input_data=self.data, batch_size=1)

            # Lets try update the state here
            forecast_state = sess.run(self.initial_state,
                                      feed_dict={self.batch_size_: 1})
            for forecast_batch, (forecast_input, forecast_target) in enumerate(forecast_generator):
                current_forecast, forecast_state = sess.run(
                    [self.prediction, self.final_state],
                    feed_dict={self.input_: forecast_input,
                               self.batch_size_: 1,
                               self.initial_state: forecast_state,
                               self.is_training: False})
                forecast.append(current_forecast.item())

            # Reconstruct the data and forecast
            self.rescaled_forecast = self.denormaliser(forecast)
            forecast_size = len(self.rescaled_forecast)
            smoothed_forecast = (
                pd.Series(
                    lowess(endog=self.rescaled_forecast,
                           exog=range(forecast_size),
                           return_sorted=False,
                           frac=float(self.forecast_period) / forecast_size))
                .reset_index(drop=True))

            complete_dates = (
                pd.date_range(rnn_start_date + timedelta(self.forecast_period + self.timestep_size),
                              periods=forecast_size)
                .to_series().reset_index(drop=True))

            self.prediction_df = pd.DataFrame(
                {'date': complete_dates,
                 'prediction': smoothed_forecast,
                 'forecastPeriod': param.forecast_period,
                 'model': 'lstm_k_step'
                 })

    def plot_prediction(self, plot_output=True):
        '''Method to plot the prediction, smoothed prediction against the
        actual values.

        '''
        valid_start = self.train_data.shape[0] + self.forecast_period
        valid_end = -self.forecast_period
        plot_df = self.prediction_df[:]
        plot_df['raw_prediction'] = self.rescaled_forecast
        padded_actual = (
            self.denormaliser(
                self.data[self.response_col].iloc[self.timestep_size:])
            .append(pd.Series([np.nan] * self.forecast_period))
            .reset_index(drop=True))
        plot_df['actual'] = padded_actual

        if plot_output == 'png':
            plt.figure(figsize=(16, 9))
            plt.plot(plot_df['date'],
                     plot_df['raw_prediction'],
                     label='raw prediction')
            plt.plot(plot_df['date'],
                     plot_df['prediction'],
                     label='smoothed_prediction')
            plt.plot(plot_df['date'],
                     plot_df['actual'],
                     label='actual', linestyle='-')
            plt.axvline(plot_df['date'].iloc[valid_start],
                        color='C5', linestyle='dashed')
            plt.axvline(plot_df['date'].iloc[valid_end],
                        color='C5', linestyle='dashed')
            plt.legend(loc='upper left')
            target_path = '{}/figure/'.format(self.log_dir)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            file_loc = '{}/{}.png'.format(target_path, self.log_string)
            print('saving as {}'.format(file_loc))
            plt.savefig(file_loc)
            plt.close()
        elif plot_output == 'tensorboard':
            plt.figure(figsize=(10, 6))
            plt.plot(plot_df['date'],
                     plot_df['raw_prediction'],
                     label='raw prediction')
            plt.plot(plot_df['date'],
                     plot_df['prediction'],
                     label='smoothed_prediction')
            plt.plot(plot_df['date'],
                     plot_df['actual'],
                     label='actual', linestyle='-')
            plt.axvline(plot_df['date'].iloc[valid_start],
                        color='C5', linestyle='dashed')
            plt.axvline(plot_df['date'].iloc[valid_end],
                        color='C5', linestyle='dashed')
            plt.legend(loc='upper left')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            with tf.Session(graph=self.graph) as sess:
                image = tf.image.decode_png(buf.getvalue(), channels=4)

                # Add the batch dimension
                image = tf.expand_dims(image, 0)

                # Add image summary
                summary_op = tf.summary.image('plot', image)
                summary = sess.run(summary_op)
                writer = tf.summary.FileWriter(
                    self.log_dir + '/images/' + self.log_string)
                writer.add_summary(summary)
                writer.close()

        else:
            plt.figure(figsize=(16, 9))
            plt.show()


def output():
    date_today = datetime.today().strftime('%Y-%m-%d')
    # Harmonise data
    harmonised_article = (
        harmonise_article(pos_sentiment_col='positive_sentiment',
                          neg_sentiment_col='negative_sentiment',
                          id_col='id'))
    preprocessed_data, denormaliser = data_preprocess(
        data=harmonised_article,
        feature_size=param.feature_size,
        forecast_period=param.forecast_period)

    model = SentimentRnn(data=preprocessed_data,
                         response_col='GOI',
                         denormaliser=denormaliser,
                         forecast_period=param.forecast_period,
                         feature_size=param.feature_size,
                         timestep_size=param.timestep_size,
                         batch_size=param.batch_size,
                         num_layer=param.num_layer,
                         cell_size=param.cell_size,
                         learning_rate=param.learning_rate,
                         holdout_period=param.holdout_period,
                         epochs=param.epochs,
                         keep_prob=param.keep_prob,
                         clipping_cap=param.clipping_cap,
                         log_dir='logs/{}'.format(date_today))
    model.train()
    model.predict()
    # model.plot_prediction(plot_output='tensorboard')

    # TODO (Michael): Should return the loss as well
    return model.prediction_df
