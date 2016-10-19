# TheReadingMachine
A Mean, Lean, Reading Machine



# Sentiment Index Minimum Viable Product (MVP) #

This one-pager is a summary of the work left to produce the first prototype of the sentiment index.

1. [Extensive overview of available dictionaries](https://github.com/EST-Team-Adam/TheReadingMachine/issues/6) (Alberto): this step will entail finding publicly available dictionaries and exploring their pros and cons, including how much they are in agreement and how they could be combined, if possible at all. *(Priority: Moderate)*
2. [Identification of labeled data sources](https://github.com/EST-Team-Adam/TheReadingMachine/issues/10) (Michael): this step entails both a literature review to understand how they have been labeled and some data mining to find already labeled text basis to build sentiment index. *(Priority: Low)*
 a. Minimum Result: writing a one pager on how to combine labeled sources
 b. Stretch Goal: train a model to construct a dictionary
3. [Data Cleaning](https://github.com/EST-Team-Adam/TheReadingMachine/issues/5) (Michael & Alberto): the text now available is pretty raw. It should be cleaned and formatted to make the analysis easier. (Priority: High)
Key Word Identification (Luca & Alberto): Identify important words that describe the information contained in the article. (Priority: Moderate)
Minimum Result: TF/IDF weighting of the words in order to reduce noise and identify important terms
Stretch Goal: building a more complex model using (maybe) POS tagging.
Labeling data sources using nlp model (Luca & Marco): this step consists on identifying more refined tags for the articles. (Priority: High)
Minimum Result: Build a simple, MF based, topic model
Stretch Goal: Actually apply the model to extract meaningful topics.
Creation of commodity tags (Alberto): (Priority: High)
Minimum Result: Tag the article with the commodity they are mostly related to. 
Stretch Goal: tagging each article with multiple commodities.
Creation of location tags (Marco): Tag the relevant location(s) the article is referred to (Priority: High)
Creation of topic tags (Marco): apply the topic model to the articles (Priority: Low)
Minimum Result: extract manually some topic tags
Stretch Goal: use the topic model developed to extract the tags
Extraction and validation of sentiment index (Michael & Marco): Create a first prototype of the actual index combining the above information. (Priority: Moderate)
Minimum Result: Come up with a plan to benchmark the results. 
Stretch Goal: Building a first multi-feature model of the index. 

Both Minimum Results and Stretch Goals are to be seen in terms of the MVP construction. All the above points can be extensively expanded as described in this document [WIP].



Modularizing the Work

Work should be modularized in order to plug other components later to be able to expand the analysis. As much as possible the code should be written in a general enough way to allow new components to be plugged in. The interface will have to accept generalized arguments that should be easily extensible. This will be hard considering the time crunch and may have to be enforced post-hoc by refactoring the code committed by others to enforce the coding standards without slowing the whole team down forcing everyone to climb the learning curve.
 (Lead: Michael. Secondary: Luca)
