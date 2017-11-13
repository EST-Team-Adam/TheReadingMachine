import pickle
import controller as ctr
from flask import Flask, render_template, request
from bokeh.embed import components
from bokeh.palettes import Spectral11
from bokeh.plotting import figure
from builder import TopicModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# Load the harmonised topic sentiment data
harmonised_article = (
    ctr.harmonise_article(pos_sentiment_col='positive_sentiment',
                          neg_sentiment_col='negative_sentiment',
                          id_col='id'))

loaded_model = pickle.load(open('topic_model.pkl', 'rb'))
analyzer = SentimentIntensityAnalyzer()
k = 5


def text_to_topic_sentiment():
    # input_text = request.form['text']
    input_text = request.args.get("text")
    print(input_text)
    # print(input_text)
    mypalette = Spectral11[:k]
    p = figure(width=1200, height=500, x_axis_type="datetime")
    if input_text is not None:
        processed_text = ctr.text_processor(text=input_text,
                                            remove_captalisation=True,
                                            remove_noun=True,
                                            remove_numerical=True,
                                            remove_punctuation=True,
                                            stem=False,
                                            tokenizer=None)
        joined_text = [' '.join(processed_text)]
        input_topic = ctr.get_top_topic(
            text=joined_text, k=5, model=loaded_model)

        topic_label = input_topic.index.tolist()

        input_topic_series = harmonised_article[topic_label]
        input_topic_series.index = harmonised_article.date
        for i in range(k):
            smoothed = input_topic_series.iloc[:, i].rolling(365).sum()
            p.line(input_topic_series.index, smoothed,
                   line_color=mypalette[i], legend='{}: {}%'.format(
                       topic_label[i], round(input_topic[i] * 100, 2)))
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
    return p


@app.route('/')
def index():
    # Create the plot
    input_text = request.args.get("text")
    if input_text is None:
        input_text = ''

    score = str(analyzer.polarity_scores(input_text)['compound'])
    # pt = processed_text()
    # topic = topic_scoring(pt)
    # plot = plot_topic_sentiment(topic)
    plot = text_to_topic_sentiment()

    # # Embed plot into HTML via Flask Render
    script, div = components(plot)
    return render_template("index.html", script=script, div=div,
                           text=input_text, score=score)



# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == '__main__':
    app.run(port=5000, debug=True)
