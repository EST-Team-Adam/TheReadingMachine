import requests
import slimit
import ast
import pandas as pd
from datetime import date
from slimit.visitors import nodevisitor
from lxml import html
from datetime import timedelta


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


def parse_goi_script(script, date_col='date'):
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
        left, right, on=date_col), df_list)

    # make the time series a regular spaced time series.
    max_date = final_data[date_col].max()
    min_date = final_data[date_col].min()
    nod = (max_date - min_date).days
    full_dates = pd.DataFrame({date_col: [min_date + timedelta(days=d)
                                          for d in range(0, nod + 1)]})

    # Interpolate the data after converting to regular spaced data
    regular_data = (
        pd.merge(final_data, full_dates, on=date_col, how='right')
        .sort_values(date_col)
        .reset_index(drop=True)
        .set_index(date_col)
        .apply(lambda x: x.interpolate('linear'), axis=0)
        .reset_index())

    return regular_data.rename(index=str, columns={'IGC': 'GOI'})
