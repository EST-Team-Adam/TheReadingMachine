from thereadingmachine.process import read_jsonl
from thereadingmachine.lexicon_modification import read_lexicon
from thereadingmachine.word_counter import wordcounter
from thereadingmachine.word_counter import wordfreq_to_dic
from thereadingmachine.word_counter import words_extraction
from thereadingmachine.lexicon_modification import contexts_extractor
from thereadingmachine.lexicon_modification import pointwise_mutual_information
from json import dump


# Initiate file names and parameters
lexicon_file="data/vader_lexicon.txt"
file_prefix = "data/amis_articles"
version = '27_11_2016'
wheat_input_file_name = '{0}_{1}_sentences_wheat.jsonl'.format(file_prefix, version)
output_file_name = 'counter_google.jsonl'.format(file_prefix, version)



# Read the data
wheat_sentences = read_jsonl(wheat_input_file_name)
lexicon = read_lexicon(lexicon_file)


# Select Words
sentences = wheat_sentences
sentences = [sentences[0][0:1100]]    # 50-1100 works


selected_words = words_extraction(sentences, lexicon)      # compares the language used in sentences with the one in google ngrams
contexts = contexts_extractor(sentences,selected_words)    # eliminate numbers from context words
contexts_lexicon = contexts_extractor(sentences,lexicon)   # computes lexicon words contexts



# Pointwise Mutual Information
wordfreq = wordfreq_to_dic(sentences)       # counter for sentences words
PMI = pointwise_mutual_information(wordfreq, contexts)
PMI_lexicon = pointwise_mutual_information(wordfreq, contexts_lexicon)