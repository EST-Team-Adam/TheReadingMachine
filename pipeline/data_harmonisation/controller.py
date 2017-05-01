import pandas as pd


def read_data_inputs(source_data_table, engine, id_field):
    table_list = list()
    for current_table in source_data_table:
        sql_query = 'SELECT * FROM {}'.format(current_table)
        table_list.append(pd.read_sql(sql_query, engine))

    merged_table = reduce(lambda x, y: pd.merge(x, y, on=id_field), table_list)

    return merged_table
