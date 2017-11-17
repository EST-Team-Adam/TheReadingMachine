import controller as ctr
from nltk import tokenize

if __name__ == '__main__':
    # --- examples -------
    sentences = ["VADER is smart, handsome, and funny.",      # positive sentence example
                 "VADER is not smart, handsome, nor funny.",   # negation sentence example
                 # punctuation emphasis handled correctly (sentiment intensity
                 # adjusted)
                 "VADER is smart, handsome, and funny!",
                 # booster words handled correctly (sentiment intensity
                 # adjusted)
                 "VADER is very smart, handsome, and funny.",
                 "VADER is VERY SMART, handsome, and FUNNY.",  # emphasis for ALLCAPS handled
                 # combination of signals - VADER appropriately adjusts
                 # intensity
                 "VADER is VERY SMART, handsome, and FUNNY!!!",
                 # booster words & punctuation make this close to ceiling for
                 # score
                 "VADER is VERY SMART, uber handsome, and FRIGGIN FUNNY!!!",
                 "The book was good.",         # positive sentence
                 # qualified positive sentence is handled correctly (intensity
                 # adjusted)
                 "The book was kind of good.",
                 # mixed negation sentence
                 "The plot was good, but the characters are uncompelling and the dialog is not great.",
                 # negated negative sentence with contraction
                 "At least it isn't a horrible book.",
                 "Make sure you :) or :D today!",     # emoticons handled
                 "Today SUX!",  # negative slang with capitalization emphasis
                 # mixed sentiment example with slang and constrastive
                 # conjunction "but"
                 "Today only kinda sux! But I'll get by, lol"
                 ]

    analyzer = ctr.SentimentIntensityAnalyzer()

    print("----------------------------------------------------")
    print(" - Analyze typical example cases, including handling of:")
    print("  -- negations")
    print("  -- punctuation emphasis & punctuation flooding")
    print("  -- word-shape as emphasis (capitalization difference)")
    print("  -- degree modifiers (intensifiers such as 'very' and dampeners such as 'kind of')")
    print("  -- slang words as modifiers such as 'uber' or 'friggin' or 'kinda'")
    print("  -- contrastive conjunction 'but' indicating a shift in sentiment; sentiment of later text is dominant")
    print("  -- use of contractions as negations")
    print("  -- sentiment laden emoticons such as :) and :D")
    print("  -- sentiment laden slang words (e.g., 'sux')")
    print("  -- sentiment laden initialisms and acronyms (for example: 'lol') \n")
    for sentence in sentences:
        vs = analyzer.polarity_scores(sentence)
        print("{:-<65} {}".format(sentence, str(vs)))
    print("----------------------------------------------------")
    print(" - About the scoring: ")
    print(""" -- The 'compound' score is computed by summing the valence scores
    of each word in the lexicon, adjusted according to the rules, and
    then normalized to be between -1 (most extreme negative) and +1
    (most extreme positive).  This is the most useful metric if you
    want a single unidimensional measure of sentiment for a given
    sentence.  Calling it a 'normalized, weighted composite score' is
    accurate.
    """)

    print(""" -- The 'pos', 'neu', and 'neg' scores are ratios for proportions
     of text that fall in each category (so these should all add up to
     be 1... or close to it with float operation).  These are the most
     useful metrics if you want multidimensional measures of sentiment
     for a given sentence.""")

    print("----------------------------------------------------")

    # input("\nPress Enter to continue the demo...\n")  # for DEMO purposes...

    tricky_sentences = ["Sentiment analysis has never been good.",
                        "Sentiment analysis has never been this good!",
                        "Most automated sentiment analysis tools are shit.",
                        "With VADER, sentiment analysis is the shit!",
                        "Other sentiment analysis tools can be quite bad.",
                        "On the other hand, VADER is quite bad ass!",
                        "Roger Dodger is one of the most compelling variations on this theme.",
                        "Roger Dodger is one of the least compelling variations on this theme.",
                        "Roger Dodger is at least compelling as a variation on the theme."
                        ]

    print("----------------------------------------------------")

    print(" - Analyze examples of tricky sentences that cause trouble to other sentiment analysis tools.")

    print("  -- special case idioms - e.g., 'never good' vs 'never this good', or 'bad' vs 'bad ass'.")
    print("  -- special uses of 'least' as negation versus comparison \n")

    for sentence in tricky_sentences:
        vs = analyzer.polarity_scores(sentence)
        print("{:-<69} {}".format(sentence, str(vs)))
    print("----------------------------------------------------")

    # input("\nPress Enter to continue the demo...\n")  # for DEMO purposes...

    print("----------------------------------------------------")

    print(" - VADER works best when analysis is done at the sentence level (but it can work on single words or entire novels).")

    paragraph = "It was one of the worst movies I've seen, despite good reviews. Unbelievably bad acting!! Poor direction. VERY poor production. The movie was bad. Very bad movie. VERY BAD movie!"

    print("  -- For example, given the following paragraph text from a hypothetical movie review:\n\t'{}'".format(paragraph))

    print("  -- You could use NLTK to break the paragraph into sentence tokens for VADER, then average the results for the paragraph like this: \n")

    # simple example to tokenize paragraph into sentences for VADER

    sentence_list = tokenize.sent_tokenize(paragraph)
    paragraphSentiments = 0.0
    for sentence in sentence_list:
        vs = analyzer.polarity_scores(sentence)
        print("{:-<69} {}".format(sentence, str(vs["compound"])))
        paragraphSentiments += vs["compound"]

    print("AVERAGE SENTIMENT FOR PARAGRAPH: \t" +
          str(round(paragraphSentiments / len(sentence_list), 4)))

    print("----------------------------------------------------")

    # input("\nPress Enter to continue the demo...\n")  # for DEMO purposes...

    print("----------------------------------------------------")

    print(" - Analyze sentiment of IMAGES/VIDEO data based on annotation 'tags' or image labels. \n")

    conceptList = ["balloons", "cake", "candles", "happy birthday",
                   "friends", "laughing", "smiling", "party"]
    conceptSentiments = 0.0

    for concept in conceptList:
        vs = analyzer.polarity_scores(concept)
        print("{:-<15} {}".format(concept, str(vs['compound'])))
        conceptSentiments += vs["compound"]

    print("AVERAGE SENTIMENT OF TAGS/LABELS: \t" +
          str(round(conceptSentiments / len(conceptList), 4)))
    print("\t")

    conceptList = ["riot", "fire", "fight",
                   "blood", "mob", "war", "police", "tear gas"]
    conceptSentiments = 0.0
    for concept in conceptList:
        vs = analyzer.polarity_scores(concept)
        print("{:-<15} {}".format(concept, str(vs['compound'])))
        conceptSentiments += vs["compound"]
    print("AVERAGE SENTIMENT OF TAGS/LABELS: \t" +
          str(round(conceptSentiments / len(conceptList), 4)))
    print("----------------------------------------------------")
