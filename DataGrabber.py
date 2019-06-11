import h5py
import matplotlib
#matplotlib.use('agg')  #Workaround for missing tkinter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import urllib
import time
import datetime
import timeit
import requests

debug = False

def read_URL_to_file (URL, filename):
    with urllib.request.urlopen(URL) as url_returns:
        data = url_returns.read().decode('utf-8').split('\n')
        with open(filename, 'w') as f:
            for datum in data:
                f.write("%s\n" % datum)
                
    return 
one_day = datetime.timedelta(days=1)
one_hour = datetime.timedelta(hours = 1)
one_sec = datetime.timedelta(seconds=1)

# utc offset (cdt)
utc_offset = datetime.timedelta(hours=5);

end   = datetime.datetime(2019, 6, 11, 0, 0);

# loop over accessible history (10 days)
for _ in xrange(10): 
    starttime = '{0:%Y-%m-%d+%H:%M:%S}'.format(end-utc_offset - one_day)
    stopptime = '{0:%Y-%m-%d+%H:%M:%S}'.format(end-utc_offset)
    end = end - one_day;

    # logger_get ACL command documentation: https://www-bd.fnal.gov/issues/wiki/ACLCommandLogger_get
    URL = "http://www-ad.fnal.gov/cgi-bin/acl.pl?acl=logger_get/date_format='utc_seconds'/ignore_db_format/start=\""+starttime+"\"/end=\""+stopptime+"\"/node="

    D43DataLoggerNode = 'MLrn'
    URL = URL + D43DataLoggerNode + '+'
    deviceNames = ['B:VIMIN', 'B_VIMIN', 'B:VIMAX', 'B_VIMAX', 'B:IMINER', 'B:NGMPS', 'B:VINHBT', 'B:GMPSFF', 'B:GMPSBT',
                   'B:IMINST', 'B:IPHSTC', 'B:IMINXG', 'B:IMINXO', 'B:IMAXXG', 'B:IMAXXO', 'B_VINHBT', 'B_GMPSFF', 'B_GMPSBT',
                   'B_IMINST', 'B_IPHSTC', 'B_IMINXG', 'B_IMINXO', 'B_IMAXXG', 'B_IMAXXO',
                   'B:ACMNPG', 'B:ACMNIG', 'B:ACMXPG', 'B:ACMXIG', 'B:DCPG' , 'B:DCIG', 'B:VIPHAS',
                   'B_ACMNPG', 'B_ACMNIG', 'B_ACMXPG', 'B_ACMXIG', 'B_DCPG' , 'B_DCIG', 'B_VIPHAS',
                   'B:PS1VGP', 'B:PS1VGM', 'B:GMPS1V', 'B:PS2VGP', 'B:PS2VGM', 'B:GMPS2V', 'B:PS3VGP', 'B:PS3VGM', 'B:GMPS3V', 'B:PS4VGP', 'B:PS4VGM', 'B:GMPS4V']
    tempfilename = 'temp_file.txt'
    timestamps = np.zeros(shape=(1,1))

    dfdict = {} #Need a place to keep each dataframe
    for deviceName in deviceNames:
        tempfilename = 'tempfile'+deviceName+'.txt'
        tempURL = URL + deviceName
        if debug: print (tempURL)

        # Download device data to local ASCII file
        with open(tempfilename, "wb") as file:
            # Column headers
            headers = 'utc_seconds'+deviceName+' \t '+deviceName+'\n'
            # Write headers encoded
            file.write(headers.encode('utf-8'))
            # Get request
            response = requests.get(tempURL)
            if str(response.content).count('logger_get') > 0:
                print (response.content) #Should go to a log file. 
                exit()
            # Write data to file
            file.write(response.content)
        # Dump the file into a pandas DataFrame 
        time_str = 'time_'
        columns = (time_str+deviceName, deviceName) # Will get these set up higher.
        dfdict[deviceName] = pd.read_csv(tempfilename, delim_whitespace=True, names=columns, skiprows=1)
        timestamps_thisdevice = pd.to_datetime(dfdict[deviceName][time_str+deviceName].values, unit = 's');
        dfdict[deviceName][time_str + deviceName] = timestamps_thisdevice; # convert to conventional time
        if debug: print (dfdict[deviceName])

    if debug: print (dfdict.values())
    df = pd.concat(dfdict.values(), axis=1)
    st1 = starttime.replace('+','').replace(':','').replace('-','')
    st2 = stopptime.replace('+','').replace(':','').replace('-','')
    df.to_csv(st1+'-'+st2+'.csv')