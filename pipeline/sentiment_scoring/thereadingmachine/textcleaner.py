def textcleaner(text):
    dic = {"\r" : " ",
           "         You must be                       You must be  I leave a flower here:      Efficacit et Transparence des Acteurs Europens   1999-2016." : " ",
           "Efficacit et Transparence des Acteurs Europens" : " ",
           "            EurActiv.com             " : " ",
           "/* customize styles to your web-site */ .mp_releases_box {  border: solid #999999 1px;  background-color: #FFFFFF; } #mp_releases {  font-family:Geneva, Arial, Helvetica, sans-serif;  padding-top: 0px;  position: relative;  vertical-align: bottom; } #mp_releases li {  margin-top: 3px; } #mp_releases a {  color: #0033CC;  font-size: 12px;  text-decoration: underline; } #mp_releases a:hover {  color: #CC0000;  font-size: 12px; } .ferthead {  font-size: 14px;  color: #000000; } .fertheadbox {  padding-left: 10px;  padding-top: 10px; }" : " ",
           "/*" : " ",
           "customize styles to your web-site" : " ",
           " .mp_releases_box " : " ",
           "border: solid" : " ",
           "background-color:" : " ",
           "#FFFFFF;" : " ",
           "#mp_releases" : " ",
           "font-family:Geneva" : " ",
           "Arial" : " ",
           "Helvetica" : " ",
           "sans-serif" : " ",
           "padding-top:" : " ",
           "0px" : " ",
           "1px" : " ",
           "position: relative" : " ",
           "vertical-align" : " ",
           "margin-top" : " ",
           "3px" : " ",
           "color:" : " ",
           "#0033CC" : " ",
           "12px" : " ",
           "font-size" : " ",
           "text-decoration" : " ",
           "#CC0000" : " ",
           ".ferthead" : " ",
           "14px" : " ",
           "#000000" : " ",
           ".fertheadbox" : " ",
           "padding-left:" : " ",
           "10px" : " ",
           "padding-top:" : " ",
           "   " : " ",
           "#999999" : " ",
           "background-" : " ",
           "a:hover" : " ",
           "}  box {" : " ",
           "underline;" : " ",
           "bottom;" : " ",
           "//" : " ",
           "}   {" : " ",
           "} li {" : " ",
           "} a {" : " ",
           "} {" : " ",
           ",  ," : " ",
           ",  ;" : " ",
           "   ;" : " ",
           "; :" : " ",
           "               " : " ",
           "\'s" : " ",
           "\\" : " ",
           "        You must be" : " ",
           "initializetabcontent(\"wholetab\")" : " ",
           "var _bizo_data_partner_id = \"513\";" : " ",
           "var _bizo_p = ((\"https:\" == document.location.protocol) ?\"" : " ",
           "https: sjs." : " ",
           ";     " : " ",
           "var _bizo_p = ((\"https:\" == document.location.protocol) ?'" : " ",
           "\");  " : " ",
           "http: js." : " ",
           "??" : " ",
           "http: js." : " ",
           #"var _bizo_data_partner_id = "513" var _bizo_p = (("https:" == document.location.protocol) ?" : " ",
           #"Home About RSS Commodities Companies Markets Subscribe Legal disclaimer Privacy policy Contact Acknowledgements Start Tab Content script for UL with id="maintab"" : " ",
           #"1999-2016." : " ",
           #"More e.g." : " ",
           #"teknoloji, teknoloji haber, mobil teknoloji" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           #"" : " ",
           "????  ??? ??????????? ??????? ???????????? ????  ??? ??????????? ??????? ????????????" : " ",
           "document.write(unescape(\"%3Cscript src=\'\" + _bizo_p + \"bizographics.com/convert_data.js?partner_id=\" + _bizo_data_partner_id + \"\' type=\'text/javascript\'%3E%3C/script%3E" : " "
           }
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
    
    

def articles_cleaner(articles, strings):                            # cleans the articles set from articles containing the strings
    strings = ['Green Plains EU grains output to revive','best crop bets', 'big bearish wheat bet','wheat futures dodge bullet'] 
    articles1 = list()
    for article in articles:
        if any(string in article['article'] for string in strings):
           articles.pop(articles.index(article))
    articles1 = articles
    return articles1
    
    
    
def articles_duplicates(articles):     # eliminate
    new_list = list()
    removed = list()
    articles1 = list()
    counter = 0
    #texts = list()
    for article in articles:
        #texts.append(article['article'])
        #counter = counter + 1
    #texts1 = list(set(texts))
        if article['article'] not in new_list:
           new_list.append(article['article'])
        else:
           counter = counter + 1
           articles.pop(articles.index(article))
           removed.append(article['article'])
           print counter
    articles1 = articles
    return articles1
    
def articles_duplicates(articles): 
    texts = [None] * len(articles)
    indexes = [None] * len(articles)  
    for article in articles:
        counter = counter + 1
        print counter
        texts.append(article['article'])
        indexes.append(articles.index(article))
    sorted(set(texts), key=texts.index)
