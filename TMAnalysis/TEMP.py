# TEMP FILE FOR TESTING FUNCTIONS

# Import modules and functions
from GRCMI import Connect
from Gateway.CreateRawNF import CreateRawNF

# Establish database connection
server_name = "https://granta.ndc.nasa.gov"
db_key = "NasaGRC_MD_45_09-2-05"
table_name = "Test Data: Thermomechanical"
mi, db, table = Connect(server_name, db_key, table_name)

# Get a record
attribute = table.attributes['Specimen ID']
search = attribute.search_criterion(equal_to='IVHM316-79')
records = table.search_for_records_where([search])
record = records[0] 

# Write to raw neutral file
CreateRawNF(record)

