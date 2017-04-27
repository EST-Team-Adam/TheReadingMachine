def textcleaner(text):
    dic = {"\r" : " ",
           "         You must be                       You must be  I leave a flower here:      Efficacit et Transparence des Acteurs Europens   1999-2016." : " ",
           "Efficacit et Transparence des Acteurs Europens" : " ",
           "            EurActiv.com             " : " "
           }
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text