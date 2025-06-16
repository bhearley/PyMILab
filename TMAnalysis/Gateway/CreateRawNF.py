#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   CreateRawNF.py
#
#   PURPOSE: Create the raw data nuetral file from Granta MI
#    
#   INPUTS:
#       record      Granta MI Record
#       fname       Temporary file name for saving
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def CreateRawNF(record, fname):
    # Import Modules
    import json
    import numpy as np
    import os
    from GRCMI import UnitConversion


    # Create the Temp Directory
    try:
        os.makedirs(os.path.join(os.getcwd(),'TMAnalysis','Gateway','Temp'))
    except:
        pass

    # Open the raw data template file
    raw_template = os.path.join(os.getcwd(),'TMAnalysis','Templates','Raw_Template.json')
    f = open(raw_template) 
    Raw = json.load(f) 

    # Open the configuration file
    config_file = os.path.join(os.getcwd(),'TMAnalysis','Gateway','config.json')
    g = open(config_file) 
    Config = json.load(g) 

    # Set Standardized Units
    Raw['Raw Data']['Units']['Time']['Value'] = 's'
    Raw['Raw Data']['Units']['Displacement']['Value'] = 'mm'
    Raw['Raw Data']['Units']['Load']['Value'] = 'N'
    Raw['Raw Data']['Units']['Strain']['Value'] = '-'
    Raw['Raw Data']['Units']['Stress']['Value'] = 'Pa'
    Raw['Raw Data']['Units']['Temperature']['Value'] = '°C'

    # Get List of Populated Functional Attributes
    for attribute in record.attributes:
        if record.attributes[attribute].type == 'FUNC':
            if len(record.attributes[attribute].value) > 1:
                # Get the name
                fields = attribute.split( ' vs ')
                if len(fields) == 2:
                    if fields[0] in Config.keys() and fields[1] in Config.keys():
                        # Get the arrays
                        x_array = []
                        y_array = []
                        for i in range(1,len(record.attributes[attribute].value)):
                            x_array.append(record.attributes[attribute].value[i][2])
                            y_array.append(record.attributes[attribute].value[i][0])

                        # Get the units
                        x_unit = record.attributes[attribute].parameters[list(record.attributes[attribute].parameters.keys())[0]].unit
                        y_unit = record.attributes[attribute].unit

                        # Appy conversion
                        x_array = UnitConversion(x_unit, np.array(x_array), eval('Raw' + Raw['Raw Data'][Config[fields[1]]]['UnitsLink'] + '["Value"]'))
                        y_array = UnitConversion(y_unit, np.array(y_array), eval('Raw' + Raw['Raw Data'][Config[fields[0]]]['UnitsLink'] + '["Value"]'))

                        # Write Value
                        Raw['Raw Data'][Config[fields[1]]]['Value'] = list(x_array)
                        Raw['Raw Data'][Config[fields[0]]]['Value'] = list(y_array)

    # Save to temp folder
    class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                dtypes = (np.datetime64, np.complexfloating)
                if isinstance(obj, dtypes):
                    return str(obj)
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    if any([np.issubdtype(obj.dtype, i) for i in dtypes]):
                        return obj.astype(str).tolist()
                    return obj.tolist()
                return super(NpEncoder, self).default(obj)

    with open(os.path.join(os.getcwd(),'TMAnalysis','Gateway','Temp', fname), "w") as outfile: 
        json.dump(Raw, outfile, cls=NpEncoder)

    return