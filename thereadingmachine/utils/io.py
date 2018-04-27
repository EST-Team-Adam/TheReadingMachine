import pandas as pd
import thereadingmachine.environment as env


def read_table(table_name, dates=True):
    sql_query = 'SELECT * FROM {}'.format(table_name)
    if dates:
        table = pd.read_sql(sql_query, env.engine, parse_dates=['date'])
    else:
        table = pd.read_sql(sql_query, env.engine)
    return table


def save_table(data, table_name, table_field_type=None):
    data.to_sql(con=env.engine,
                name=table_name,
                index=False,
                if_exists='replace',
                dtype=table_field_type)
