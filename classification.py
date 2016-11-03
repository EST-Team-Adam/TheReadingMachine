import json
from nltk.corpus import reuters
from sklearn.metrics import confusion_matrix
from thereadingmachine.classify import create_tfidf_training_data
from thereadingmachine.classify import train_svm


# Reading data
# --------------------------------------------------

# Initiate file names and parameters
file_prefix = "data/amis_articles"
version = '27_07_2016'
input_file_name = '{0}_{1}_processed.jsonl'.format(file_prefix, version)
test_sample_size = 1000

# Read the data
print "Reading data from '{0}' ...".format(input_file_name)
articles = []
with open(input_file_name) as f:
    for line in f:
        articles.append(json.loads(line))

# Take a sample for testing
test_sample = articles[:test_sample_size]

# Data preparation
# --------------------------------------------------

# Obtain Reuters labelled data
topic = ['wheat', 'corn', 'maize', 'rice', 'soybean']
labelled_file = reuters.fileids(topic)

labelled_set = [(categories, reuters.raw(file))
                for file in labelled_file
                for categories in reuters.categories(file)
                if categories in topic]

# Extract the unlabelled text
unlabelled_set = [('', article['article']) for article in test_sample]


# Now combine the list.
#
# NOTE (Michael): We need to combine the list in order to ensure the
#                 tfidf matrix is of the same dimesion.
total_set = labelled_set + unlabelled_set
full_x, full_y = create_tfidf_training_data(total_set)

# Split into training and predict set
labelled_index = [ind for ind, y in enumerate(full_y) if y != '']
unlabelled_index = [ind for ind, y in enumerate(full_y) if y == '']

# The training contained labelled data while the test does not
train_x = full_x[labelled_index, ]
train_y = [full_y[ind] for ind in labelled_index]
test_x = full_x[unlabelled_index, ]
test_y = [full_y[ind] for ind in unlabelled_index]


# Train the classification model
# --------------------------------------------------
train_model = train_svm(train_x, train_y)
train_pred = train_model.predict(train_x)
print(train_model.score(train_x, train_y))
print(confusion_matrix(train_pred, train_y))

# Since we don't have the labelling, we have to manually check them.
test_pred = train_model.predict(test_x)

# TODO (Michael): Need to map the predicted back to the original
#                 articles.
