import requests
import slimit
import ast
import pandas as pd
from datetime import date
from slimit.visitors import nodevisitor
from lxml import html


def extract_goi_page():
    ''' This function extracts the javascript text where the data is hold.
    '''

    page = requests.get("http://www.igc.int/en/markets/marketinfo-goi.aspx")
    tree = html.fromstring(page.content)
    script = tree.xpath('//script[@type="text/javascript"]/text()')
    return script


def goi_list_to_df(data, name):
    ''' This function parses the data list into a pandas data frame.
    '''

    d = list()
    p = list()

    for l in data:
        parsed_date = date(l[0][0], l[0][1] + 1, l[0][2])
        d.append(parsed_date)
        p.append(l[1])
    return pd.DataFrame({'date': d, name: p})


def parse_goi_script(script):
    '''Extract the data node from the javascript text, then parse each
    individual price and then merge to create the final data frame.

    '''

    parser = slimit.parser.Parser()
    tree = parser.parse(script[0])
    fields = [node
              for node in nodevisitor.visit(tree)
              if isinstance(node, slimit.ast.Array)]

    var_names = [ast.literal_eval(node.to_ecma()).split(' ')[0]
                 for node in nodevisitor.visit(fields[0])
                 if isinstance(node, slimit.ast.String)]

    series = [ast.literal_eval(node.to_ecma().replace('Date.UTC', ''))
              for node in nodevisitor.visit(fields[0])
              if isinstance(node, slimit.ast.Array)
              and len(node.to_ecma()) > 1000]

    df_list = [goi_list_to_df(d, n) for n, d in zip(var_names, series)]

    final_data = reduce(lambda left, right: pd.merge(
        left, right, on='date'), df_list)

    return final_data.rename(index=str, columns={'IGC': 'GOI'})
