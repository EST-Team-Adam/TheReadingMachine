import thereadingmachine.scraper.price_scraper as ctr
import thereadingmachine.environment as env
import thereadingmachine.utils.io as io

# Obtain data
goi_script = ctr.extract_goi_page()
price_data = ctr.parse_goi_script(goi_script)

# save data
io.save_table(data=price_data,
              table_name=env.price_table,
              table_field_type=env.price_field_type)
