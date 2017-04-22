import nltk
import string

def remove_propers_POS(s):
    tagged = nltk.pos_tag(s.split()) #use NLTK's part of speech tagger
    non_propernouns = [word for word,pos in tagged if pos != 'NNP' and pos != 'NNPS']
    return ''.join([n + " " for n in non_propernouns])

def preprocessor(s):
    s = remove_propers_POS(s)
    # remove numericals and punctuation
    s = "".join([c if c not in string.punctuation else ' ' for c in s if not c.isdigit()])
    s = s.lower()
    return s
