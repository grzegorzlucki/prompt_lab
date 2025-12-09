import sqlite3

conn = sqlite3.connect('trips.sqlite')
cursor = conn.cursor()

fixes = [
    ('calendar_dates', '\ufeffservice_id', 'service_id'),
    ('contracts_ext', '\ufeffcontract_id', 'contract_id'),
    ('shapes', '\ufeffshape_id', 'shape_id'),
    ('vehicle_types', '\ufeffvehicle_type_id', 'vehicle_type_id'),
    ('feed_info', '\ufefffeed_publisher_name', 'feed_publisher_name'),
    ('variants', '\ufeffvariant_id', 'variant_id'),
    ('control_stops', '\ufeffvariant_id', 'variant_id'),
    ('calendar', '\ufeffservice_id', 'service_id'),
    ('routes', '\ufeffroute_id', 'route_id'),
    ('route_types', '\ufeffroute_type2_id', 'route_type2_id')
]

for table, old_col, new_col in fixes:
    cursor.execute(f'ALTER TABLE {table} RENAME COLUMN "{old_col}" TO {new_col}')
    print(f"Fixed {table}")

conn.commit()
conn.close()

print("\nAll tables fixed!")
