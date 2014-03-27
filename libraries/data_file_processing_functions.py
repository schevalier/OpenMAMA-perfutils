import numpy as np
from matplotlib import cm
from sys import exit
from collectlParserlib import get_collectl_proc_data, find_start_time, offset_all_seconds_since_epoch_timestamps, get_collectl_CPU_data, get_collectl_network_data
import dateutil.parser
import time
from re import search,match,split
from os import listdir
import ptpd2_parser_lib
#----------------------------------------------------------------------
# Load and process collectl file for process cpu utilization
# If start_time is -1 or not passed in then the earliest timestamp (in seconds since epoch GMT) of any process matching the process filter will be used as start_time.
# After offsetting by the start_time, the first head and last tail seconds of data are filtered out
# A dictionary is returned containing filtered time and CPU data for every process
#----------------------------------------------------------------------
def process_collectl_file_processes(collectl_file,proc_filter,head,tail,start_time=-1):
    print "Processing collectl log file for processes."
    #Load collectl file and get data for processes matching proc_filter
    collectl_data=get_collectl_proc_data(collectl_file,proc_filter)
    #Convert EDT to UTC
    #collectl_data=offset_all_seconds_since_epoch_timestamps(collectl_data,-14400)
    #Convert ET to UTC
    #collectl_data=offset_all_seconds_since_epoch_timestamps(collectl_data,-18000)
    #Set start time if required
    if start_time==-1:
        start_time=find_start_time(collectl_data)
        print "Set start time as",start_time
    #Offset data so that start time = 0
    collectl_data=offset_all_seconds_since_epoch_timestamps(collectl_data,start_time)
    #Setup dictionaries for filtering data and calculting stats
    filtered_collectl_data={}

    percentiles={}
    stats={}
    filter={}
    non_numeric_keys=['User','PR','Date','Time','S','AccuTime','Command']
    numeric_keys=['SysT', 'Pct', 'UsrT',  'THRD', 'PID',   'CP', 'PPID','seconds_since_epoch' ]
    scaled_numeric_keys=['VSZ','RSS','MajF','MinF','WKB','RKB','VmSize','VmLck','VmRSS','VmData','VmStk','VmExe','VmLib','VmSwp']
    scalers={'K':1000,'M':1000000,'G':1000000000,'T':1000000000000}

    #For each process in the collectl_data, filter for the time period of interest and calculate stats
    keys=collectl_data.keys()
    for key in keys:
        if key not in filtered_collectl_data and key not in non_numeric_keys:
            filtered_collectl_data[key]={}
        processes=collectl_data[key].keys()
        for process in processes:
            #Create logical filter based on period of interest
            filter=(np.array(collectl_data['seconds_since_epoch'][process],dtype=float)>=head) & (np.array(collectl_data['seconds_since_epoch'][process],dtype=float)<=tail)
            #Filter data and cast cpu data as int (extracted as string from collectl file)
            if key in numeric_keys:
                filtered_collectl_data[key][process]={}
                filtered_collectl_data[key][process]=np.array(collectl_data[key][process],dtype=float)[filter]
                if key is 'Pct':
                #Calculate percentiles at 0.1% resolution and calculate stats
                    percentiles[process]=calc_hi_res_percentiles(filtered_collectl_data[key][process],10000)
                    stats[process]=calc_stats(filtered_collectl_data[key][process])
            elif key in scaled_numeric_keys:
                filtered_collectl_data[key][process]={}
                scaled_values=np.zeros(len(collectl_data[key][process]))
                for i,value in enumerate(collectl_data[key][process]):
                    if value[-1] in scalers:
                        scaled_values[i]=int(value[0:-1])*scalers[value[-1]]
                    else:
                        scaled_values[i]=int(value)
                filtered_collectl_data[key][process]=scaled_values[filter]

            #    filtered_collectl_data[key][process]=np.array(collectl_data[key][process])[filter]
    #Exit if no data was loaded
    if len(filtered_collectl_data['seconds_since_epoch'])==0:
        print "No valid collectl data loaded."

    #Return data, start_time must be returned in case it was altered
    return filtered_collectl_data,stats,percentiles,start_time

#----------------------------------------------------------------------
# Load and process collectl file for CPU.
# If start_time is -1 or not passed in then the earliest timestamp (in seconds since epoch GMT) of any process matching the process filter will be used as start_time.
# After offsetting by the start_time, the first head and last tail seconds of data are filtered out
# A dictionary is returned containing the filtered data for all fields for every CPU
#----------------------------------------------------------------------
def process_collectl_file_cpu(collectl_file,head,tail,start_time=-1):
    print "Processing collectl log file for CPU."
    #Load collectl file and get data
    collectl_data=get_collectl_CPU_data(collectl_file)
    #Convert EDT to UTC
    #collectl_data=offset_all_seconds_since_epoch_timestamps(collectl_data,-14400)
    #Convert ET to UTC
    #collectl_data=offset_all_seconds_since_epoch_timestamps(collectl_data,-18000)
    #Set start time if required
    if start_time==-1:
        start_time=find_start_time(collectl_data)
        print "Set start time as",start_time
    #Offset data so that start time = 0
    collectl_data=offset_all_seconds_since_epoch_timestamps(collectl_data,start_time)
    #Setup dictionaries for filtering data and calculting stats
    filtered_collectl_data={}
    filter={}
    for name in collectl_data['seconds_since_epoch']:
        filter[name]=(np.array(collectl_data['seconds_since_epoch'][name],dtype=float)>=head) & (np.array(collectl_data['seconds_since_epoch'][name],dtype=float)<=tail)
    #For each field in the collectl_data, filter for the time period of interest
    for field in collectl_data:
        filtered_collectl_data[field]={}
        for name in collectl_data[field]:
            #Filter data and cast numeric data as float (extracted as string from collectl file)
            filtered_collectl_data[field][name]=np.array(collectl_data[field][name],dtype=float)[filter[name]]
    #Exit if no data was loaded
    if len(filtered_collectl_data['seconds_since_epoch'])==0:
        print "No valid collectl data loaded."

    #Return data, start_time must be returned in case it was altered
    return filtered_collectl_data,start_time

#----------------------------------------------------------------------
# Load and process collectl file for Network.
# If start_time is -1 or not passed in then the earliest timestamp (in seconds since epoch GMT) of any process matching the process filter will be used as start_time.
# After offsetting by the start_time, the first head and last tail seconds of data are filtered out
# A dictionary is returned containing the filtered data for all fields for every named network device
#----------------------------------------------------------------------
def process_collectl_file_network(collectl_file,head,tail,start_time=-1):
    print "Processing collectl log file for network."
    #Load collectl file and get data
    collectl_data=get_collectl_network_data(collectl_file)
    #Convert EDT to UTC
    #collectl_data=offset_all_seconds_since_epoch_timestamps(collectl_data,-14400)
    #Convert ET to UTC
    #collectl_data=offset_all_seconds_since_epoch_timestamps(collectl_data,-18000)
    #Remove name field as it is of no use and causes problems with filtering
    del collectl_data['Name']
    #Set start time if required
    if start_time==-1:
        start_time=find_start_time(collectl_data)
        print "Set start time as",start_time
    #Offset data so that start time = 0
    collectl_data=offset_all_seconds_since_epoch_timestamps(collectl_data,start_time)
    #Setup dictionaries for filtering data and calculting stats
    filtered_collectl_data={}
    filter={}
    for name in collectl_data['seconds_since_epoch']:
        filter[name]=(np.array(collectl_data['seconds_since_epoch'][name],dtype=float)>=head) & (np.array(collectl_data['seconds_since_epoch'][name],dtype=float)<=tail)
    #For each field in the collectl_data, filter for the time period of interest
    for field in collectl_data:
        filtered_collectl_data[field]={}
        for name in collectl_data[field]:
            #Filter data and cast as int (extracted as string from collectl file)
            filtered_collectl_data[field][name]=np.array(collectl_data[field][name],dtype=float)[filter[name]]

    #Exit if no data was loaded
    if len(filtered_collectl_data['seconds_since_epoch'])==0:
        print "No valid collectl data loaded."

    #Return data, start_time must be returned in case it was altered
    return filtered_collectl_data,start_time


#----------------------------------------------------------------------
#Load and process feed handler logs
#If start_time is -1 or not passed in then the earliest timestamp (in seconds since epoch GMT) with non-zero WIMP message rate of the first (alphabetical) file matching file_filter will be used as start_time.
#After offsetting by the start_time, the first head and last tail seconds of data are filtered out
#----------------------------------------------------------------------
def process_feedhandler_logs(file_filter,head,tail,stats_interval=5,path='./',start_time=-1,add_extension=True):
    print "Processing feed handler log files."
    start_time=0
    #Get list of files and setup dictionaries for data
    files=listdir(path)
    files.sort(reverse=True)
    feed_handler_log_data={'Msg. Rates':{},'Gap Rates':{}}

    num_missed=0
    #For each file, check if it matches the filter and then extract the data
    if add_extension:
        file_filter+='.*\.log'
    for filename in files:
        #Check if the current file matches the file_filter and has .log extension
        if search(file_filter,filename):
            print "Processing file: " + filename
            #Open the file
            rfp=open(path + filename,'r')
            #Initialise empty arrays for this file in the dictionaries
            mama_message_times=[]
            mama_message_rates=[]
            gap_times=[]
            gap_rates=[]
            num_missed=0
            mama_message_rate=0
            first_block_time=0
            interval=0
            interval_time=0
            #Get the first line
            line=rfp.readline()
            while line!="":
                if match(r"Info:[ ]+[0-9]{4}/[0-9]{2}/[0-9]{2}",line):
                    timestamp=search(r"[0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}",line).group(0)
                    dt=dateutil.parser.parse(timestamp)
                    seconds_since_epoch=time.mktime(dt.timetuple())
                    #print "timestamp: ",timestamp," in seconds: ",seconds_since_epoch
                    if first_block_time==0:
                        first_block_time=seconds_since_epoch
                        #print "first_block_time: "+str(seconds_since_epoch)
                    else:
                        interval=seconds_since_epoch-first_block_time
                        interval_time=seconds_since_epoch
                        #print "interval is "+str(interval)
                        rfp.seek(-1, 1)
                        break

                line=rfp.readline()

            #Loop over lines
            while line!="":
                #Find start of stats block
                if match(r"Info:[ ]+[0-9]{4}/[0-9]{2}/[0-9]{2}",line):
                    #If any gaps were detected in the previous stats block, normalise the rates to the stats_interval (--stats-interval=stats_interval) and record them
                    if num_missed>0:
                        gap_times.append(seconds_since_epoch)
                        gap_rates.append(num_missed/stats_interval)

                    #Extract timestamp and convert to seconds since epoch
                    timestamp=search(r"[0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}",line).group(0)
                    dt=dateutil.parser.parse(timestamp)
                    seconds_since_epoch=time.mktime(dt.timetuple())
                    interval=seconds_since_epoch-interval_time
                    interval_time=seconds_since_epoch
                    #Convert EDT to UTC
                    #seconds_since_epoch+=14400
                    #Convert ET to UTC
                    #seconds_since_epoch-=18000
                    #Set start time if required
                    if start_time==-1:
                        start_time=seconds_since_epoch
                        #print "Set start time as",start_time
                        #Offset the timestamp by the start_time
                    seconds_since_epoch=seconds_since_epoch-start_time
                    #Set the message rate and number of missed messages for this interval to 0
                    num_missed=0
                    mama_message_rate=0
                #Check if current line is a MamaMessageCount line and process process message rate if it is.
                #I think this is only reported once per interval. If it can occur more than once then the append code will need to be moved into the preceeding block like the gap append has been
                #elif match(r"Info:[ ]+MamaMessageCount",line):
                elif match(r"Info:[ ]+Publisher\(default\) statistics",line):
                    #Extract the mama message count and normalise it to the stats_interval (--stats-interval=stats_interval)
                    #mama_message_rate=float(search(r"(MamaMessageCount.\([a-zA-Z]+\) |[ ]+)([0-9]+)",line).group(2))/stats_interval
                    mama_message_rate=float(search(r"number=([0-9]+)",line).group(1))/stats_interval
                    #If the log message occurs within the period of interest (set by head and tail), then record it
                    if (seconds_since_epoch>head) & (seconds_since_epoch<tail):
                        mama_message_times.append(seconds_since_epoch)
                        mama_message_rates.append(mama_message_rate)
                #Process gaps if any are present
                elif match(r"Error: LineFilter\(.*\): permanently missed ",line):
                    if start_time != -1:
                        if (seconds_since_epoch>head) & (seconds_since_epoch<tail):
                            #Extract number of missed messages
                            num_missed+=float(search(r"(missed )([0-9]+)",line).group(2))
                #Get the next line
                line=rfp.readline()

            #Log any gaps that occured in the final stats block of the file
            if search(file_filter + '.*log',filename):
                if num_missed>0:
                    gap_rates.append(num_missed/stats_interval)

            feed_handler_log_data['Msg. Rates'][filename]=[mama_message_times,mama_message_rates]
            if len(gap_rates)>0:
                feed_handler_log_data['Gap Rates'][filename]=[gap_times,gap_rates]

    #for filename in feed_handler_log_data['Msg. Rates'].keys():
    #    print "Mean feed handler message rate for",filename,"was",int(np.round(np.average(feed_handler_log_data['Msg. Rates'][filename]))),"messages per second."
    #Log if no data was loaded
    if len(feed_handler_log_data['Msg. Rates'].keys())==0:
        print "No valid feed handler logs loaded."

    #Return data, start_time must be returned in case it was altered
    return feed_handler_log_data,start_time

#----------------------------------------------------------------------
#Load and process feed handler logs
#If start_time is -1 or not passed in then the earliest timestamp (in seconds since epoch GMT) with non-zero WIMP message rate of the first (alphabetical) file matching file_filter will be used as start_time.
#After offsetting by the start_time, the first head and last tail seconds of data are filtered out
#----------------------------------------------------------------------
def process_superfeed_cache_logs(file_filter,head,tail,stats_interval=5,path='./',start_time=-1,add_extension=True):
    print "Processing cache log files."
    #Get list of files and setup dictionaries for data
    files=listdir(path)
    files.sort(reverse=True)
    feed_handler_log_data={'Msg. Rates':{},'Gap Rates':{},'Update Rates':{},'Symbol Request Rates':{},'Subscription Request Rates':{}}
    num_missed=0
    #For each file, check if it matches the filter and then extract the data
    for filename in files:
        #Check if the current file matches the file_filter and has .log extension
        if add_extension:
            file_filter+='.*\.log'

        if search(file_filter,filename):
            print "Processing file: " + filename
            #Open the file
            rfp=open(path + filename,'r')
            #Initialise empty arrays for this file in the dictionaries
            generic_update_times=[]
            generic_update_rates=[]
            mama_message_times=[]
            mama_message_rates=[]
            symbol_request_times=[]
            symbol_request_rates=[]
            subscription_request_times=[]
            subscription_request_rates=[]
            gap_times=[]
            gap_rates=[]
            num_missed=0
            generic_update_rate=0
            mama_message_rate=0
            #Get the first line
            line=rfp.readline()
            #Loop over lines, in this case, just get the counts and don't normalise to interval. The stats interval and rates will be calculated later from the coutns and timestamps
            while line!="":
                #Find start of stats block
                if match(r"[0-9]{2}:[0-9]{2}:[0-9]{2} Info:[ ]+[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}",line):
                    #If any gaps or updates were detected in the previous stats block, normalise the rates to the stats_interval (--stats-interval=stats_interval) and record them
                    if num_missed>0:
                        gap_times.append(seconds_since_epoch)
                        gap_rates.append(num_missed)
                    if generic_update_rate>0:
                        generic_update_times.append(seconds_since_epoch)
                        generic_update_rates.append(generic_update_rate)
                    #Extract timestamp and convert to seconds since epoch
                    timestamp=search(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}",line).group(0)
                    dt=dateutil.parser.parse(timestamp)
                    seconds_since_epoch=time.mktime(dt.timetuple())
                    #Convert EDT to UTC
                    #seconds_since_epoch+=14400
                    #Convert ET to UTC
                    #seconds_since_epoch-=18000
                    #Set start time if required
                    if start_time==-1:
                        start_time=seconds_since_epoch
                        print "Set start time as",start_time
                        #Offset the timestamp by the start_time
                    #seconds_since_epoch=seconds_since_epoch-start_time

                    #Set the message rate and number of missed messages for this interval to 0
                    num_missed=0
                    generic_update_rate=0
                    mama_message_rate=0
                    symbol_request_rate=0
                    subscription_request_rate=0
                #Check if current line is a MamaMessageCount line and process  message rate if it is.
                #I think this is only reported once per interval. If it can occur more than once then the append code will need to be moved into the preceeding block like the gap append has been
                elif match(r"[0-9]{2}:[0-9]{2}:[0-9]{2} Info:[ ]+MamaMessageCount",line):
                    #Extract the mama message count
                    mama_message_rate=float(search(r"(MamaMessageCount.\([a-zA-Z]+\) |[ ]+)([0-9]+)",line).group(2))
                    #If the log message occurs within the period of interest (set by head and tail), then record it
                    if (seconds_since_epoch>head) & (seconds_since_epoch<tail):
                        mama_message_times.append(seconds_since_epoch)
                        mama_message_rates.append(mama_message_rate)
                #Check if current line is a SymbolRequest line and process  rate if it is.
                #I think this is only reported once per interval. If it can occur more than once then the append code will need to be moved into the preceeding block like the gap append has been
                elif match(r"[0-9]{2}:[0-9]{2}:[0-9]{2} Info:[ ]+SymbolRequest",line):
                    #Extract the symbol request count
                    symbol_request_rate=float(search(r"(SymbolRequest.\([a-zA-Z]+\) |[ ]+)([0-9]+)",line).group(2))
                    #If the log message occurs within the period of interest (set by head and tail), then record it
                    if (seconds_since_epoch>head) & (seconds_since_epoch<tail):
                        symbol_request_times.append(seconds_since_epoch)
                        symbol_request_rates.append(symbol_request_rate)
                #Check if current line is a subsc-req line and process  rate if it is.
                #I think this is only reported once per interval. If it can occur more than once then the append code will need to be moved into the preceeding block like the gap append has been
                elif match(r"[0-9]{2}:[0-9]{2}:[0-9]{2} Info:[ ]+subsc-req",line):
                    #Extract the subscription request count
                    subscription_request_rate=float(search(r"(=)([0-9]+)",line).group(2))
                    #If the log message occurs within the period of interest (set by head and tail), then record it
                    if (seconds_since_epoch>head) & (seconds_since_epoch<tail):
                        subscription_request_times.append(seconds_since_epoch)
                        subscription_request_rates.append(subscription_request_rate)
                #Process updates (messages in) if any are present
                elif match(r"[0-9]{2}:[0-9]{2}:[0-9]{2} Info:[ ]+[a-zA-Z]+Update",line):
                    #If the log update occurs within the period of interest (set by head and tail), then record it
                    if (seconds_since_epoch>head) & (seconds_since_epoch<tail):
                        #Extract the genric update count
                        generic_update_rate+=float(search(r"(Update.\([a-zA-Z]+\) |[ ]+)([0-9]+)",line).group(2))
                #Process gaps if any are present
                elif match(r"[0-9]{2}:[0-9]{2}:[0-9]{2} Error: LineFilter\(.*\): permanently missed ",line):
                    if start_time != -1:
                        if (seconds_since_epoch>head) & (seconds_since_epoch<tail):
                            #Extract number of missed messages
                            num_missed+=float(search(r"(missed )([0-9]+)",line).group(2))
                #Get the next line
                line=rfp.readline()

            #Log any gaps or updates that occured in the final stats block of the file
            if search(file_filter + '.*log',filename):
                if num_missed>0:
                    gap_times.append(seconds_since_epoch)
                    gap_rates.append(num_missed)
                if generic_update_rate>0:
                    generic_update_times.append(seconds_since_epoch)
                    generic_update_rates.append(generic_update_rate)
            #Add data to the dictionary
            feed_handler_log_data['Msg. Rates'][filename]=[mama_message_times,mama_message_rates]
            print 'Msg rate: ',len(feed_handler_log_data['Msg. Rates'][filename][0])

            feed_handler_log_data['Update Rates'][filename]=[generic_update_times,generic_update_rates]
            print 'Update rate: ',len(feed_handler_log_data['Update Rates'][filename][0])

            if len(symbol_request_rates)>0:
                feed_handler_log_data['Symbol Request Rates'][filename]=[symbol_request_times,symbol_request_rates]
                print 'Symbol rate: ',len(feed_handler_log_data['Symbol Request Rates'][filename][0])

            if len(subscription_request_rates)>0:
                feed_handler_log_data['Subscription Request Rates'][filename]=[subscription_request_times,subscription_request_rates]
                print 'Subscription rate: ',len(feed_handler_log_data['Subscription Request Rates'][filename][0])

            if len(gap_rates)>0:
                feed_handler_log_data['Gap Rates'][filename]=[gap_times,gap_rates]
            #Calculate intervals and rates
            intervals=[]
            for i in range(1,len(feed_handler_log_data['Msg. Rates'][filename][0])):
                intervals.append(feed_handler_log_data['Msg. Rates'][filename][0][i]-feed_handler_log_data['Msg. Rates'][filename][0][i-1])
            feed_handler_log_data['Msg. Rates'][filename][0]=feed_handler_log_data['Msg. Rates'][filename][0][1:]
            feed_handler_log_data['Msg. Rates'][filename][1]=np.divide(feed_handler_log_data['Msg. Rates'][filename][1][1:],intervals)

            #Calculate intervals and rates
            intervals=[]
            if filename in feed_handler_log_data['Symbol Request Rates'].keys():
                print 'Adding symbol requests'

                for i in range(1,len(feed_handler_log_data['Symbol Request Rates'][filename][0])):
                    intervals.append(feed_handler_log_data['Symbol Request Rates'][filename][0][i]-feed_handler_log_data['Symbol Request Rates'][filename][0][i-1])
                feed_handler_log_data['Symbol Request Rates'][filename][0]=feed_handler_log_data['Symbol Request Rates'][filename][0][1:]
                feed_handler_log_data['Symbol Request Rates'][filename][1]=np.divide(feed_handler_log_data['Symbol Request Rates'][filename][1][1:],intervals)

            #Calculate intervals and rates
            #intervals=[]
            #if filename in feed_handler_log_data['Subscription Request Rates'].keys():
            #    print 'Adding subscription requests'
            #    for i in range(1,len(feed_handler_log_data['Subscription Request Rates'][filename][0])):
            #        intervals.append(feed_handler_log_data['Subscription Request Rates'][filename][0][i]-feed_handler_log_data['Subscription Request Rates'][filename][0][i-1])
            #    feed_handler_log_data['Subscription Request Rates'][filename][0]=feed_handler_log_data['Subscription Request Rates'][filename][0][1:]
            #    feed_handler_log_data['Subscription Request Rates'][filename][1]=np.divide(feed_handler_log_data['Subscription Request Rates'][filename][1][1:],intervals)


            intervals=[]
            for i in range(1,len(feed_handler_log_data['Update Rates'][filename][0])):
                intervals.append(feed_handler_log_data['Update Rates'][filename][0][i]-feed_handler_log_data['Update Rates'][filename][0][i-1])
            feed_handler_log_data['Update Rates'][filename][0]=feed_handler_log_data['Update Rates'][filename][0][1:]
            feed_handler_log_data['Update Rates'][filename][1]=np.divide(feed_handler_log_data['Update Rates'][filename][1][1:],intervals)

            intervals=[]
            if filename in feed_handler_log_data['Gap Rates'].keys():
                for i in range(1,len(feed_handler_log_data['Gap Rates'][filename][0])):
                    intervals.append(feed_handler_log_data['Gap Rates'][filename][0][i]-feed_handler_log_data['Gap Rates'][filename][0][i-1])
                feed_handler_log_data['Gap Rates'][filename][0]=feed_handler_log_data['Gap Rates'][filename][0][1:]
                feed_handler_log_data['Gap Rates'][filename][1]=np.divide(feed_handler_log_data['Gap Rates'][filename][1][1:],intervals)

    #for filename in feed_handler_log_data['Msg. Rates'].keys():
    #    print "Mean feed handler message rate for",filename,"was",int(np.round(np.average(feed_handler_log_data['Msg. Rates'][filename]))),"messages per second."
    #Log if no data was loaded
    if len(feed_handler_log_data['Msg. Rates'].keys())==0:
        print "No valid feed handler logs loaded."


    #Return data, start_time must be returned in case it was altered
    return feed_handler_log_data,start_time

#----------------------------------------------------------------------
#Load and process tick file for HTH line time and receive time differences
#If start_time is -1 or not passed in then the earliest reference linetime timestamp (in seconds since epoch GMT) will be used as the start time.
#After offsetting by the start_time, the first head and last tail seconds of data are filtered out
#This version should work for tickrecorder running with gtod or rdtsc
#----------------------------------------------------------------------
def process_tick_file_with_4_times_for_HTH_diffs(file_filter,head,tail,path='./',start_time=-1):
    print "Processing tick file."
    #Get list of files
    files=listdir(path)
    files.sort(reverse=True)

    #Find and open the first file that matches the file_filter and has .npz extension
    for filename in files:
        if search(file_filter + '.npz',filename):
            print "Loading tick file", filename
            try:
                #Load the file
                npfile=np.load(filename)
                break
            #Exit if an IO exception occurs while loading the file
            except IOError as (errno, strerror) :
                print("Attempted to load invalid tick file. Exiting.")
                exit()

    #Extract the original data file names (without extensions) and the tick sequence numbers. These are not used or returned at the moment.
    #data_title1=npfile["data_title_1"]
    #data_title1=npfile["data_title_2"]
    seq_nums=[]
    try:
        seq_nums=np.array(npfile["seq_nums"],dtype=np.int)
    except:
        pass

    #Extract the 4 timestamps as linetimes and receive times.
    ref_linetimes=np.array(npfile["ref_time_1"],dtype=np.int)
    ref_recvtimes=np.array(npfile["ref_time_2"],dtype=np.int)
    test_linetimes=np.array(npfile["test_time_1"],dtype=np.int)
    test_recvtimes=np.array(npfile["test_time_2"],dtype=np.int)

    #Delete the loaded file just in case it saves some memory
    del npfile

    #Convert reference linetimes to seconds since epoch and use as timestamps for filtering and plotting
    linetimes_s=np.divide(ref_linetimes,1000000.0)
    #linetimes_s=np.divide(ref_recvtimes,1000000.0)

    #Set start time if required (using easrliest reference linetime)
    if start_time==-1:
        #Timezone offset for tickrecorder data recorded in ET
        start_time=linetimes_s[0]-18000
        #Offset the timestamp by the start_time and ET-GMT
        linetimes_s=np.subtract(linetimes_s,linetimes_s[0])
        print "Set start time as",start_time
    else:
        #Offset the timestamp by the start_time and ET-GMT
        linetimes_s=np.subtract(linetimes_s,start_time+18000)

    #Create logical filter based on period of interest
    filter=(linetimes_s>head) & (linetimes_s<tail)
    #Filter data
    linetimes_s=linetimes_s[filter]
    ref_linetimes=ref_linetimes[filter]
    ref_recvtimes=ref_recvtimes[filter]
    test_linetimes=test_linetimes[filter]
    test_recvtimes=test_recvtimes[filter]

    #Calculate head-to-head latency differences for linetime and receive time
    linetime_diffs=np.subtract(ref_linetimes,test_linetimes)
    rectime_diffs=np.subtract(ref_recvtimes,test_recvtimes)

    #Calculate the duration of the tick file, this only works if the timestamps start at zero and needs fixing
    duration=calc_duration(linetimes_s)
    print("Duration of tick file = " + str(duration) + " seconds")
    #Calculate the 1 second average match rates
    print("Calculating match rate..."),
    match_rate=calc_rolling_match_rate(linetimes_s,0.01)
    print "Mean match rate was", int(np.rint(np.average(match_rate))), "messages/second"

    #Calculate the linetime and receive time latency difference stats
    lt_stats=calc_stats(linetime_diffs)
    lt_percentiles=calc_hi_res_percentiles(linetime_diffs,1001)
    rt_stats=calc_stats(rectime_diffs)
    rt_percentiles=calc_hi_res_percentiles(rectime_diffs,1001)

    #Return the data
    return linetimes_s,linetime_diffs,rectime_diffs,match_rate,lt_stats,lt_percentiles,rt_stats,rt_percentiles,seq_nums,start_time

#----------------------------------------------------------------------
#Load and process tick file for HTH line time and receive time differences
#If start_time is -1 or not passed in then the earliest reference linetime timestamp (in seconds since epoch GMT) will be used as the start time.
#After offsetting by the start_time, the first head and last tail seconds of data are filtered out
#This version should work for tickrecorder running with gtod or rdtsc
#----------------------------------------------------------------------
def process_tick_file_with_6_times_for_HTH_diffs(file_filter,head,tail,path='./',start_time=-1):
    print "Processing tick file."
    #Get list of files
    files=listdir(path)
    files.sort(reverse=True)
    #Find and open the first file that matches the file_filter and has .npz extension
    for filename in files:
        if search(file_filter + '.npz',filename):
            print "Loading tick file", filename
            try:
                #Load the file
                npfile=np.load(filename)
                break
            #Exit if an IO exception occurs while loading the file
            except IOError as (errno, strerror) :
                print("Attempted to load invalid tick file. Exiting.")
                exit()
    mamasenderids=[]
    try:
        mamasenderids=np.array(npfile["mamasenderids"],dtype=np.int)
    except:
        pass
    #Extract the original data file names (without extensions) and the tick sequence numbers. These are not used or returned at the moment.
    #data_title1=npfile["data_title_1"]
    #data_title1=npfile["data_title_2"]

    #Extract the 6 timestamps as linetimes, receive times and sendtimes.
    seq_nums=np.array(npfile["seq_nums"],dtype=np.int)
    ref_linetimes=np.array(npfile["ref_time_1"],dtype=np.int)
    ref_recvtimes=np.array(npfile["ref_time_2"],dtype=np.int)
    ref_sendtimes=np.array(npfile["ref_time_3"],dtype=np.int)
    test_linetimes=np.array(npfile["test_time_1"],dtype=np.int)
    test_recvtimes=np.array(npfile["test_time_2"],dtype=np.int)
    test_sendtimes=np.array(npfile["test_time_3"],dtype=np.int)

    #Delete the loaded file just in case it saves some memory
    del npfile

    #Convert reference linetimes to seconds since epoch and use as timestamps for filtering and plotting
    linetimes_s=np.divide(ref_linetimes,1000000.0)

    #Set start time if required (using easrliest reference linetime)
    if start_time==-1:
        #Timezone offset for tickrecorder data recorded in ET
        start_time=linetimes_s[0]-18000
        #Offset the timestamp by the start_time and ET-GMT
        linetimes_s=np.subtract(linetimes_s,linetimes_s[0])
        print "Set start time as",start_time
    else:
        #Offset the timestamp by the start_time and ET-GMT
        linetimes_s=np.subtract(linetimes_s,start_time+18000)

    #Create logical filter based on period of interest
    filter=(linetimes_s>head) & (linetimes_s<tail)
    #Filter data
    linetimes_s=linetimes_s[filter]
    seq_nums=seq_nums[filter]
    ref_linetimes=ref_linetimes[filter]
    ref_recvtimes=ref_recvtimes[filter]
    ref_sendtimes=ref_sendtimes[filter]
    test_linetimes=test_linetimes[filter]
    test_recvtimes=test_recvtimes[filter]
    test_sendtimes=test_sendtimes[filter]
    if len(mamasenderids)>0:
        mamasenderids=mamasenderids[filter]
    #Calculate head-to-head latency differences for linetime and receive time
    ref_fhlatency=np.subtract(ref_sendtimes,ref_linetimes)
    test_fhlatency=np.subtract(test_sendtimes,test_linetimes)
    fhlatency_diffs=np.subtract(ref_fhlatency,test_fhlatency)
    linetime_diffs=np.subtract(ref_linetimes,test_linetimes)
    sendtime_diffs=np.subtract(ref_sendtimes,test_sendtimes)
    rectime_diffs=np.subtract(ref_recvtimes,test_recvtimes)

    #Calculate the duration of the tick file, this only works if the timestamps start at zero and needs fixing
    duration=calc_duration(linetimes_s)
    print("Duration of tick file = " + str(duration) + " seconds")
    #Calculate the 1 second average match rates
    print("Calculating match rate..."),
    match_rate=calc_rolling_match_rate(linetimes_s,1)
    print "Mean match rate was", int(np.rint(np.average(match_rate))), "messages/second"

    #Calculate the linetime and receive time latency difference stats
    fh_stats=calc_stats(fhlatency_diffs)
    fh_percentiles=calc_percentiles(fhlatency_diffs)
    rt_stats=calc_stats(rectime_diffs)
    rt_percentiles=calc_percentiles(rectime_diffs)

    #Return the data
    return linetimes_s,ref_fhlatency,test_fhlatency,linetime_diffs,sendtime_diffs,rectime_diffs,match_rate,fh_stats,fh_percentiles,rt_stats,rt_percentiles,start_time,seq_nums,mamasenderids


#----------------------------------------------------------------------
#Load and process tick file for RTT segment latencies
#If start_time is -1 or not passed in then the earliest reference linetime timestamp (in seconds since epoch GMT) will be used as the start time.
#After offsetting by the start_time, the first head and last tail seconds of data are filtered out
#This version should work for tickrecorder running with gtod or rdtsc, though the udp and ibv segments will be invalid for rdtsc or non-synched gtod
#----------------------------------------------------------------------
def process_tick_file_with_4_times_for_RTT_latencies(file_filter,head,tail,path='./',start_time=-1,stats=True):
    print "Processing tick file."
    #Get list of files
    files=listdir(path)
    files.sort(reverse=True)
    #Find and open the first file that matches the file_filter and has .npz extension
    for filename in files:
        if search(file_filter + '.npz',filename):
            print "Loading tick file", filename
            try:
                #Load the file
                npfile=np.load(filename)
                break
            #Exit if an IO exception occurs while loading the file
            except IOError as (errno, strerror) :
                print("Attempted to load invalid tick file. Exiting.")
                exit()

    #Extract the 4 timestamps
    mamasender_ids=[]
    try:
        mamasender_ids=npfile["mamasender_ids"]
    except:
        pass
    send_times=npfile["send_times"]
    rec_times=npfile["recv_times"]
    line_times=npfile["line_times"]
    mamasend_times=npfile["mamasend_times"]
    seq_nums=npfile["seq_nums"]
    #Delete the loaded file just in case it saves some memory
    del npfile

    #Convert sendtimes to seconds since epoch and use as timestamps for filtering and plotting
    time_s=np.divide(send_times,1000000.0)

    #Set start time if required (using earliest sendtimes)
    if start_time==-1:
        #Timezone offset for tickrecorder data recorded in ET
        start_time=time_s[0]-18000
        #Offset the timestamp by the start_time and ET-GMT
        time_s=np.subtract(time_s,time_s[0])
        print "Set start time as",start_time
    else:
        #Offset the timestamp by the start_time and ET-GMT
        time_s=np.subtract(time_s,start_time+18000)

    #Create logical filter based on period of interest
    filter=(time_s>head) & (time_s<tail)
    #Filter data
    time_s=time_s[filter]
    send_times=send_times[filter]
    rec_times=rec_times[filter]
    line_times=line_times[filter]
    mamasend_times=mamasend_times[filter]
    seq_nums=seq_nums[filter]

    if len(mamasender_ids)!=0:
        mamasender_ids=mamasender_ids[filter]

    rt_latency=rec_times-send_times
    udp_latency=line_times-send_times
    fh_latency=mamasend_times-line_times
    ibv_latency=rec_times-mamasend_times

    #Calculate the duration of the tick file, this only works if the timestamps start at zero and needs fixing
    duration=calc_duration(time_s)
    print("Duration of tick file = " + str(duration) + " seconds")
    #Calculate the 1 second average match rates
    print("Calculating match rate..."),
    match_rate=calc_rolling_match_rate(time_s,1)
    print "Mean match rate was", int(np.rint(np.average(match_rate))), "messages/second"

    #Calculate various statistics from the data and return as a dictionary
    all_stats={}
    if stats is True:
        print "Calculating statistics: "
        all_stats['rt_stats']=calc_stats(rt_latency)
        all_stats['rt_percentiles']=calc_percentiles(rt_latency)
        all_stats['udp_stats']=calc_stats(udp_latency)
        all_stats['udp_percentiles']=calc_percentiles(udp_latency)
        all_stats['fh_stats']=calc_stats(fh_latency)
        all_stats['fh_percentiles']=calc_percentiles(fh_latency)
        all_stats['ibv_stats']=calc_stats(ibv_latency)
        all_stats['ibv_percentiles']=calc_percentiles(ibv_latency)

    #Return the data
    return time_s,rt_latency,udp_latency,fh_latency,ibv_latency,match_rate,all_stats,start_time,mamasender_ids,seq_nums



#----------------------------------------------------------------------
#Load and process tick file for RTT segment latencies
#If start_time is -1 or not passed in then the earliest reference linetime timestamp (in seconds since epoch GMT) will be used as the start time.
#After offsetting by the start_time, the first head and last tail seconds of data are filtered out
#This version should work for tickrecorder running with gtod or rdtsc, though the udp and ibv segments will be invalid for rdtsc or non-synched gtod
#----------------------------------------------------------------------
def process_tick_file_with_4_times_for_RTT_timestamps(file_filter,head,tail,path='./',start_time=-1,stats=True):
    print "Processing tick file."
    #Get list of files
    files=listdir(path)
    files.sort(reverse=True)
    #Find and open the first file that matches the file_filter and has .npz extension
    for filename in files:
        if search(file_filter + '.npz',filename):
            print "Loading tick file", filename
            try:
                #Load the file
                npfile=np.load(filename)
                break
            #Exit if an IO exception occurs while loading the file
            except IOError as (errno, strerror) :
                print("Attempted to load invalid tick file. Exiting.")
                exit()

    #Extract the 4 timestamps
    mamasender_ids=[]
    try:
        mamasender_ids=npfile["mamasender_ids"]
    except:
        pass
    send_times=npfile["send_times"]
    rec_times=npfile["recv_times"]
    line_times=npfile["line_times"]
    mamasend_times=npfile["mamasend_times"]
    seq_nums=npfile["seq_nums"]
    #Delete the loaded file just in case it saves some memory
    del npfile

    #Convert sendtimes to seconds since epoch and use as timestamps for filtering and plotting
    time_s=np.divide(send_times,1000000.0)

    #Set start time if required (using earliest sendtimes)
    if start_time==-1:
        #Timezone offset for tickrecorder data recorded in ET
        start_time=time_s[0]-18000
        #Offset the timestamp by the start_time and ET-GMT
        time_s=np.subtract(time_s,time_s[0])
        print "Set start time as",start_time
    else:
        #Offset the timestamp by the start_time and ET-GMT
        time_s=np.subtract(time_s,start_time+18000)

    #Create logical filter based on period of interest
    filter=(time_s>head) & (time_s<tail)
    #Filter data
    time_s=time_s[filter]
    send_times=send_times[filter]
    rec_times=rec_times[filter]
    line_times=line_times[filter]
    mamasend_times=mamasend_times[filter]
    seq_nums=seq_nums[filter]

    if len(mamasender_ids)!=0:
        mamasender_ids=mamasender_ids[filter]



    #Return the data
    return time_s,send_times,line_times,mamasend_times,rec_times,start_time,mamasender_ids,seq_nums





#----------------------------------------------------------------------
#Load and process tick file for feed handler internal latency
#If start_time is -1 or not passed in then the earliest reference linetime timestamp (in seconds since epoch GMT) will be used as the start time.
#After offsetting by the start_time, the first head and last tail seconds of data are filtered out
#This version should work for tickrecorder running with gtod or rdtsc
#----------------------------------------------------------------------
def process_tick_file_with_2_times_for_fh_latency(file_filter,head,tail,path='./',start_time=-1):
    print "Processing tick file."
    #Get list of files
    files=listdir(path)
    files.sort(reverse=True)
    #Find and open the first file that matches the file_filter and has .npz extension
    for filename in files:

        if search(file_filter + '.npz',filename):
            print "Loading tick file", filename
            try:
                #Load the file
                npfile=np.load(filename)
                break
            #Exit if an IO exception occurs while loading the file
            except IOError as (errno, strerror) :
                print("Attempted to load invalid tick file. Exiting.")
                exit()

    #Extract the original data file names (without extensions) and the tick sequence numbers. These are not used or returned at the moment.
    #data_title1=npfile["data_title_1"]
    #data_title1=npfile["data_title_2"]
    #seq_nums=np.array(npfile["seq_nums"],dtype=np.int)
    mamasenderids=[]
    try:
        mamasenderids=np.array(npfile["mamasenderids"],dtype=np.int)
    except:
        pass

    #Extract the 4 timestamps as linetimes and receive times.
    linetimes=np.array(npfile["linetime"],dtype=np.int)
    sendtimes=np.array(npfile["sendtime"],dtype=np.int)
    latencies=np.array(npfile["latency"],dtype=np.int)

    #Delete the loaded file just in case it saves some memory
    del npfile

    #Convert reference linetimes to seconds since epoch and use as timestamps for filtering and plotting
    linetimes_s=np.divide(linetimes,1000000.0)

    #Set start time if required (using easrliest reference linetime)
    if start_time==-1:
        #Timezone offset for tickrecorder data recorded in ET
        start_time=linetimes_s[0]-18000
        #Offset the timestamp by the start_time and ET-GMT
        linetimes_s=np.subtract(linetimes_s,linetimes_s[0])
        print "Set start time as",start_time
    else:
        #Offset the timestamp by the start_time and ET-GMT
        linetimes_s=np.subtract(linetimes_s,start_time+18000)

    #Create logical filter based on period of interest
    filter=(linetimes_s>head) & (linetimes_s<tail)
    #Filter data
    linetimes_s=linetimes_s[filter]
    linetimes=linetimes[filter]
    sendtimes=sendtimes[filter]
    latencies=latencies[filter]
    if len(mamasenderids)>0:
        mamasenderids=mamasenderids[filter]
    #Calculate the duration of the tick file, this only works if the timestamps start at zero and needs fixing
    duration=calc_duration(linetimes_s)
    print("Duration of tick file = " + str(duration) + " seconds")
    #Calculate the 1 second average match rates
    print("Calculating match rate..."),
    match_rate=calc_match_rate(linetimes_s,duration)
    print "Mean match rate was", int(np.rint(np.average(match_rate))), "messages/second"

    #Calculate the linetime and receive time latency difference stats
    stats=calc_stats(latencies)
    percentiles=calc_percentiles(latencies)

    #Return the data
    return linetimes_s,latencies,match_rate,stats,percentiles,start_time,mamasenderids

#----------------------------------------------------------------------
#Load and process single tick file
#If start_time is -1 or not passed in then the earliest reference linetime timestamp (in seconds since epoch GMT) will be used as the start time.
#After offsetting by the start_time, the first head and last tail seconds of data are filtered out
#This version should work for tickrecorder running with gtod or rdtsc
#----------------------------------------------------------------------
def process_tick_file(file_filter,head,tail,path='./',start_time=-1):
    print "Processing tick file."
    #Get list of files
    files=listdir(path)
    files.sort(reverse=True)
    #Find and open the first file that matches the file_filter and has .npz extension
    for filename in files:

        if search(file_filter + '.npz',filename):
            print "Loading tick file", filename
            try:
                #Load the file
                npfile=np.load(filename)
                break
            #Exit if an IO exception occurs while loading the file
            except IOError as (errno, strerror) :
                print("Attempted to load invalid tick file. Exiting.")
                exit()


    #Extract the 4 timestamps as linetimes and receive times.
    linetimes=np.array(npfile["linetimes"],dtype=np.int)
    mamasendtimes=np.array(npfile["mamasendtimes"],dtype=np.int)
    rectimes=np.array(npfile["rectimes"],dtype=np.int)
    mamasenderids=np.array(npfile["mamasenderids"],dtype=np.int)
    seqnums=np.array(npfile["seqnums"],dtype=np.int)

    #Delete the loaded file just in case it saves some memory
    del npfile

    #Convert reference linetimes to seconds since epoch and use as timestamps for filtering and plotting
    linetimes_s=np.divide(linetimes,1000000.0)

    #Set start time if required (using easrliest reference linetime)
    if start_time==-1:
        #Timezone offset for tickrecorder data recorded in ET
        start_time=linetimes_s[0]-18000
        #Offset the timestamp by the start_time and ET-GMT
        linetimes_s=np.subtract(linetimes_s,linetimes_s[0])
        print "Set start time as",start_time
    else:
        #Offset the timestamp by the start_time and ET-GMT
        linetimes_s=np.subtract(linetimes_s,start_time+18000)

    #Create logical filter based on period of interest
    filter=(linetimes_s>head) & (linetimes_s<tail)
    #Filter data
    linetimes_s=linetimes_s[filter]
    linetimes=linetimes[filter]
    mamasendtimes=mamasendtimes[filter]
    rectimes=rectimes[filter]
    mamasenderids=mamasenderids[filter]
    seqnums=seqnums[filter]
    #Calculate the duration of the tick file, this only works if the timestamps start at zero and needs fixing
    duration=calc_duration(linetimes_s)
    print("Duration of tick file = " + str(duration) + " seconds")
    #Calculate the 1 second average match rates
    #Calculate the 1 second average match rates
    print("Calculating match rate..."),
    match_rate=calc_rolling_match_rate(linetimes_s,1)
    print "Mean match rate was", int(np.rint(np.average(match_rate))), "messages/second"


    #Return the data
    return linetimes_s,linetimes,mamasendtimes,rectimes,mamasenderids,seqnums,match_rate,start_time


#----------------------------------------------------------------------
#Load and process ptpd2 file
#If start_time is -1 or not passed in then the earliest timestamp (in seconds since epoch GMT) will be used as the start time.
#After offsetting by the start_time, the first head and last tail seconds of data are filtered out
#----------------------------------------------------------------------
def process_ptpd2_file(ptpd2_file,head,tail,start_time=-1):
    ptpd2_data=ptpd2_parser_lib.get_ptpd2_data(ptpd2_file)
    filtered_ptpd2_data={}
    filtered_ptpd2_data['seconds_since_epoch']=np.zeros(len(ptpd2_data['# Timestamp']))

    print 'Calculating seconds since epoch timestamps'
    for i,timestamp in enumerate(ptpd2_data['# Timestamp']):
        dt=dateutil.parser.parse(timestamp)
        filtered_ptpd2_data['seconds_since_epoch'][i]=time.mktime(dt.timetuple())+(dt.time().microsecond/1000000.0)

    print 'Filtering start and end time'
    if start_time==-1:
        start_time=filtered_ptpd2_data['seconds_since_epoch'][0]
        print "Set start time as",start_time
    #Offset data so that start time = 0
    filtered_ptpd2_data['seconds_since_epoch']=np.subtract(filtered_ptpd2_data['seconds_since_epoch'],start_time)
    filter=(filtered_ptpd2_data['seconds_since_epoch']>=head) & (filtered_ptpd2_data['seconds_since_epoch']<=tail)
    filtered_ptpd2_data['seconds_since_epoch']=filtered_ptpd2_data['seconds_since_epoch'][filter]
    fields=ptpd2_data.keys()
    numeric_keys=['One Way Delay','Offset From Master','Slave to Master','Master to Slave','Drift','Ofm Mean','Ofm Std Dev','Drift Std Dev']
    non_numeric_keys=['# Timestamp','State','Clock ID','Last packet Received']
    for key in fields:
        if key in numeric_keys:
            filtered_ptpd2_data[key]=np.array(ptpd2_data[key],dtype=float)[filter]

    return filtered_ptpd2_data,start_time


#--------------------------------------------------------------------
#Calculate data set duration assuming data start at t=0
#--------------------------------------------------------------------
def calc_duration(match_times):
    return int(np.ceil(max(match_times)))


#--------------------------------------------------------------------
#Calculate 1 second average match rates
#--------------------------------------------------------------------
def calc_match_rate(times,duration):

    match_rates=np.zeros(duration,dtype=int)

    interval_data=np.array(np.floor(times),dtype=int)



    for i in interval_data:
        match_rates[i]+=1

    #np.delete(match_rates,duration-1)

    return match_rates

#--------------------------------------------------------------------
#Calculate match rates using rolling window (in seconds)
#--------------------------------------------------------------------
def calc_rolling_match_rate(times,window):

    match_rates=np.zeros(len(times),dtype=int)

    window_start_time_index=0

    for i,time in enumerate(times):
        if time-times[window_start_time_index]<window:
            if window_start_time_index==i:
                match_rates[i]=1
            else:
                match_rates[i]=i-window_start_time_index
        else:
            while time-times[window_start_time_index]>window and window_start_time_index < i :
                window_start_time_index+=1
            if window_start_time_index==i:
                match_rates[i]=1
            else:
                match_rates[i]=i-window_start_time_index
    return match_rates


#--------------------------------------------------------------------
#Returns a 99 element array containing the 1st through 99th percentiles
#For simplicity this function ignores the last mod(data_set,100) elements of data_set
#Therefore it is very important that data_set not be sorted when it is passed in
#--------------------------------------------------------------------
def calc_percentiles(data_set):
    #Pre-allocate percentile array
    percentiles=np.zeros(99,dtype=np.int)
    #Get array length
    data_len=len(data_set)
    #Calculate how many ticks account for 1% of the data
    els_per_percent=int(np.floor(data_len/100))
    #Sort the data (quicksort), ignoring last mod(data_set,100) elements
    ignored_els=np.fmod(data_len,100)
    sorted_data=np.sort(data_set[0:(data_len-ignored_els)])

    #Extract percentile values from sorted data
    for i in range(1,100):
        percentiles[i-1]=sorted_data[i*els_per_percent-1]

    #Return percentile array
    return percentiles

#--------------------------------------------------------------------
#Returns a 2D array of percentiles with num_bins elements [percentile,value;...]
#The first and last percentiles are always 0 and 100, respectively
#--------------------------------------------------------------------
def calc_hi_res_percentiles(data_set,num_bins):
    percentiles=np.zeros([num_bins,2],dtype=np.float)
    #Sort the data (quicksort)
    data_set=np.sort(data_set)
    elements_per_percent=len(data_set)/100

    percentiles=np.transpose(np.array([np.linspace(1,100,num_bins),np.zeros(num_bins)]))
    for i in range(0,num_bins-1):
        percentiles[i][1]=data_set[int(round(percentiles[i][0]*elements_per_percent,0)-1)]
    percentiles[num_bins-1][1]=data_set[-1]
    return percentiles

#--------------------------------------------------------------------
#Returns a 101 element array containing percentage of data points at the CPU % equal to the array index
#--------------------------------------------------------------------
def calc_cpu_freq(data_set):
    bins=np.zeros(101,dtype=np.float)
    #Sort the data (quicksort)
    data_set=np.round(np.sort(data_set),0)
    if data_set[-1]>100:
        print "CPU data are not limited to 100%"
        return np.array(0)
    i=0
    j=0
    while i <= 100 and j < len(data_set):
        if data_set[j]==i:
            bins[i]+=1
            j+=1
        else:
            i+=1

    bins=np.multiply(bins,100.0/len(data_set))
    return bins

def calc_cpu_cum_freq(data_set):
    return np.cumsum(calc_cpu_freq(data_set))

#--------------------------------------------------------------------
#Returns a dictionary with min, max, avg and stdev values
#--------------------------------------------------------------------
def calc_stats(data_set):
    #Calculate statistics
    stat_set={}
    stat_set["avg"]=np.rint(np.average(data_set))
    stat_set["std"]=np.rint(np.std(data_set))
    stat_set["max"]=np.rint(np.amax(data_set))
    stat_set["min"]=np.rint(np.amin(data_set))

    return stat_set

#--------------------------------------------------------------------
# Crop data set
#--------------------------------------------------------------------
def crop_data_set(data_set,head,tail):
    return data_set[head:len(data_set)-tail-1]

#--------------------------------------------------------------------
# Check for market close
#--------------------------------------------------------------------
def check_market_close(times):
    last_time=times[0]
    closed=-1
    for i in range(1,len(times)):
        if((times[i]-last_time)>1):
            closed=i
            break
        else:
            last_time=times[i]
    return closed

#--------------------------------------------------------------------
#These functions were written to help with SHARP testing
#--------------------------------------------------------------------
# Generator to load numpy data file
# Only tested on single variable files so far
#--------------------------------------------------------------------
def load_sharp_data_file(input_file):
    print input_file
    try:
        npfile=np.load(input_file)


    except IOError as (errno, strerror) :
        print("Binary data file not detected.")
        exit()

    var_names=npfile.files


    for name in var_names:
        yield npfile[name]

#--------------------------------------------------------------------
#Mamalatency style function
#Returns 2, 20 element, arrays containing the number of points in each 50 microsecond range
#up to 950 microseconds and the percentage of points this represents.
#For simplicity this function ignores the last mod(data_set,100) elements of data_set
#Therefore it is very important that data_set not be sorted when it is passed in
#--------------------------------------------------------------------
def calc_range_counts(data_set,bin_width,num_bins):

    #Pre-allocate percentile array
    range_counts=np.zeros(num_bins,dtype=np.float)


    sorted_data=np.sort(data_set)

    #Extract percentile values from sorted data

    max_bin=(num_bins-1)*bin_width

    index=0
    cur_bin=bin_width

    for value in sorted_data:
        if value<cur_bin:
            range_counts[index]+=1
        else:

            index=int(np.ceil(value/bin_width))
            cur_bin=index*bin_width

            if cur_bin<max_bin:
                range_counts[index]+=1
            else:
                range_counts[num_bins-1]+=1

    return range_counts
#--------------------------------------------------------------------
#Mamalatency style functions
#Write files in the same format as MamaLatency
#--------------------------------------------------------------------
def write_mamaLatency_file(rf,range_counts,bin_width,data_title):

    range_percentages=100*np.divide(range_counts,sum(range_counts))
    range_cumpercentages=np.cumsum(range_percentages)
    rf.write("Range stats from file: " + data_title + "\n")
    for i in range(len(range_counts)-1):
        rf.write("Latency from\t" + '%d'%(i*bin_width) + "\tto\t" + '%d'%((i+1)*bin_width-1) + "\t" + '%d'%(range_counts[i]) + "\t" + '%.6f'%range_percentages[i] + "\t" + '%.6f'%range_cumpercentages[i] + "\n")
    i+=1
    rf.write("Latency from\t" + '%d'%(i*bin_width) + "\tto\t\t" + '%d'%(range_counts[i]) + "\t" + '%.6f'%range_percentages[i] + "\t" + '%.6f'%range_cumpercentages[i] + "\n")
    rf.write("\n\n")

def write_range_data(rf,range_counts,data_title):
    fileline="Range stats from file: " + data_title + '\t'
    for i in range_counts:
        fileline += '%d'%i + '\t'
    rf.write(fileline + '\n')
    print fileline
#--------------------------------------------------------------------

def process_mamaproducer_logs(file_filt, path):
    data={}
    wanted_headers=['RATE']
    files=listdir(path)
    files.sort(reverse=False)
    print "looking for files containing ",file_filt
    for filename in files:
        if search(file_filt,filename):
            print "processing "+filename+"..."
            data[filename]={}
            for header in wanted_headers:
                data[filename][header]=[[],[]]
            rfp=open(path + filename,'r')
            line=rfp.readline()

            # Skip down to stats lines
            while len(line)>0:
                if search(r"[0-9]{4}/[0-9]{2}/[0-9]{2} - [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2} RATE",line):
                    timesplit=split(r"([0-9]{4}/[0-9]{2}/[0-9]{2} - [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})",line)

                    timestamp=timesplit[1].strip("-")
                    dt=dateutil.parser.parse(timestamp)
                    seconds_since_epoch=time.mktime(dt.timetuple())

                    metrics=(timesplit[2].strip("\n")).split("=")
                    data[filename]['RATE'][0].append(seconds_since_epoch)
                    data[filename]['RATE'][1].append(metrics[1])

                line=rfp.readline()
            rfp.close()
    return data

def process_mamaconsumer_logs(file_filt, path, cpufreq):
    data={}
    wanted_headers=['RATE','TRANS LOW','TRANS AVG','TRANS HIGH','GAPS','MC GAPS','MISSING FIDS']
    files=listdir(path)
    files.sort(reverse=False)
    for file in files:
        if search(file,file_filt):
            data[file]={}
            for header in wanted_headers:
                data[file][header]=[[],[]]
            print "processing "+file+"..."
            rfp=open(path + file,'r')
            line=rfp.readline()

            # Skip down to header line
            while len(line)>0:
                if search ('TIME',line):
                    break
                line=rfp.readline()
            while len(line)>0:
                if search(r"[0-9]{4}/[0-9]{2}/[0-9]{2} - [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}",line):
                    timesplit=split(r"([0-9]{4}/[0-9]{2}/[0-9]{2} - [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})",line)

                    timestamp=timesplit[1].strip("-")
                    dt=dateutil.parser.parse(timestamp)
                    seconds_since_epoch=time.mktime(dt.timetuple())

                    metrics=(timesplit[2].strip("\n")).split()
                    for i,header in enumerate(wanted_headers):
                        data[file][header][0].append(seconds_since_epoch)
                        data[file][header][1].append(float(metrics[i])/cpufreq)
                line=rfp.readline()
    return data

def process_netstat_logs(file_filt, path):
    data={}
    headers=['Proto','Recv-Q','Send-Q','Local Address','Foreign Address','State']
    wanted_headers=['Recv-Q','Send-Q']
    files=listdir(path)
    files.sort(reverse=False)
    for filename in files:
        if search(file_filt,filename):
            data[filename]={}
            for header in wanted_headers:
                data[filename][header]=[[],[]]
            print "processing "+filename+"..."
            rfp=open(path + filename,'r')
            #skip header line
            line=rfp.readline()
            line=rfp.readline()
            while len(line)>0:
                if search(r"[0-9]{4}/[0-9]{2}/[0-9]{2} - [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}",line):
                    timesplit=split(r"([0-9]{4}/[0-9]{2}/[0-9]{2} - [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2})",line)
                    timestamp=timesplit[1].strip("-")
                    dt=dateutil.parser.parse(timestamp)
                    seconds_since_epoch=time.mktime(dt.timetuple())
                elif search(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:",line):
                    splitline=(line.strip("\n")).split()
                    for i,header in enumerate(headers):
                        if header in wanted_headers:
                            data[filename][header][0].append(seconds_since_epoch)
                            data[filename][header][1].append(splitline[i])
                line=rfp.readline()
    return data

