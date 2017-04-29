import csv
import langid
import sys  



reload(sys)  
sys.setdefaultencoding('utf8')



def twitter_reader(input_file_name):
    print 'Reading Twitter Data'
    twitter = []
    with open(input_file_name,  'r') as f:
         reader = csv.DictReader(f, delimiter=',')
         for line in reader:
             line['id'] = line['id']
             twitter.append(line)
    return twitter
             


def twitter_formatter(twitter_data):
    #print 'Formatting Twitter Data'
    twitter_data3 = list()
    twitter_data2 = list()
    twitter_data1 = list()
    for data in twitter_data:
        data['article'] = data.pop('text;;;;;;;;;')                  # formatting
        data['date'] = data.pop('created_at')
        twitter_data1.append({k: v for k, v in data.items() if v})          # empty tweet removal
    twitter_data3 = filter(None, twitter_data1)
    for k in twitter_data3:
        if k.get('article') == None:
           del k
        else:
           if langid.classify(k['article'])[0] in ['en']:            # non-english tweet removal TILL HERE EVERYTHING WORKS (just 30 over 102 seems a little low)
              twitter_data2.append(k)
    return twitter_data2