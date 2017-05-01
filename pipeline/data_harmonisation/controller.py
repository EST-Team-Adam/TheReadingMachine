import os
import pandas as pd
from sqlalchemy import create_engine


def read_data_inputs(source_data_table, engine, id_field):
    table_list = list()
    for current_table in source_data_table:
        sql_query = 'SELECT * FROM {}'.format(current_table)
        table_list.append(pd.read_sql(sql_query, engine))

    table_list.append(get_raw_article_with_dates())
    merged_table = reduce(lambda x, y: pd.merge(x, y, on=id_field), table_list)

    return merged_table


def get_raw_article_with_dates():
    data_dir = os.environ['DATA_DIR']
    engine = create_engine(
        'sqlite:///{0}/the_reading_machine.db'.format(data_dir))
    dated_article = pd.read_sql('SELECT id, date FROM RawArticle', engine)
    return dated_article
