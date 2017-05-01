import os
import controller as ctr
from sqlalchemy import create_engine

# Configuration
data_dir = os.environ['DATA_DIR']
source_data_table = ['TopicModel', 'CommodityTaggedArticle']
target_data_table = 'HarmonisedData'
engine = create_engine('sqlite:///{0}/the_reading_machine.db'.format(data_dir))

# Read and merge all data sources
merged_data = ctr.read_data_inputs(
    source_data_table=source_data_table, engine=engine, id_field='id')

# Save back to database
merged_data.to_sql(con=engine, name=target_data_table, index=False,
                   if_exists='replace')
