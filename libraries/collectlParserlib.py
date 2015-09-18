#!/usr/bin/env python
#_______________________________________________________________________
# Python script to parse collectl log file, very much work in progress
# Currently, -sC -sN and -sZ are supported.
# collectl must have been run with collectl -oD
# for <1s sampling interval -oDm  is required to get meaningful time-stamps
# -oT is not supported since it only records time, not date
# running with -on is not recommended as extracting the process monitoring interval is not possible
# If this is useful then more options can be supported
# Returns a:
# dictionary collectl_data which contains a
#    dictionary for each field, which contains an
#        array of strings for each process
# Type casting is left for the calling program to perform so that the parsing function here doesn't have to understand the field names
#_______________________________________________________________________

#--------------------------------------------------------------------
# Module imports
#--------------------------------------------------------------------
import re
import dateutil.parser
import time
from itertools import izip
from numpy import subtract, array,zeros

#--------------------------------------------------------------------
# Functions for handling specific collectl -s options
#--------------------------------------------------------------------
# Function for extracting CPU data collected with -sC
#--------------------------------------------------------------------
def get_collectl_CPU_data(collectl_filename):
    #Call general collectl parser with ID field = Cpu and header string '# SINGLE CPU STATISTICS'
    collectl_data=get_collectl_data(collectl_filename,'Cpu',r'# SINGLE CPU STATISTICS')
    #Remove leading hash from first field name
    collectl_data=strip_hash(collectl_data)
    #Calculate seconds since epoch field for all cpus and then remove the date and time fields
    collectl_data=add_seconds_since_epoch_field(collectl_data)
    collectl_data=remove_date_and_time_fields(collectl_data)
    #Return the dictionary containing all of the log data
    return collectl_data

#--------------------------------------------------------------------
# Function for extracting process data collected with -sZ
#--------------------------------------------------------------------
def get_collectl_proc_data(collectl_filename,filter):
    #Call general collectl parser with ID field = Command and header string '# PROCESS SUMMARY'
    collectl_data=get_collectl_data(collectl_filename,'Command',r'# PROCESS SUMMARY')
    #Remove processes not matching the regex filter (the filter may appear anywhere in the command, not just at the start)
    collectl_data=filter_data(collectl_data,filter)
    #Remove leading hash from first field name
    collectl_data=strip_hash(collectl_data)
    #Calculate seconds since epoch field for all processes and then remove the date and time fields
    collectl_data=add_seconds_since_epoch_field(collectl_data)
    #Return the dictionary containing all of the log data
    return collectl_data

#--------------------------------------------------------------------
# Function for extracting Network data collected with -sN
#--------------------------------------------------------------------
def get_collectl_network_data(collectl_filename):
    #Call general collectl parser with ID field = Name and header string '# SINGLE CPU STATISTICS'
    collectl_data=get_collectl_data(collectl_filename,'Name',r'# NETWORK STATISTICS')
    #Remove leading hash from first field name
    collectl_data=strip_hash(collectl_data)
    #Calculate seconds since epoch field for all cpus and then remove the date and time fields
    collectl_data=add_seconds_since_epoch_field(collectl_data)
    collectl_data=remove_date_and_time_fields(collectl_data)
    #Return the dictionary containing all of the log data
    return collectl_data

#--------------------------------------------------------------------
# General log parser, intended to be called by one of the functions in the previous section
#--------------------------------------------------------------------
# This function parses the collectl log
#--------------------------------------------------------------------
def get_collectl_data(collectl_filename,ID_fieldname,header_string):
    #Initialise data dictionary and field array.
    #The fields array is required to store fields in the order that they occur in the log file
    collectl_data={}
    fields=[]
    ID_field=-1
    #Open file
    collectl_log=open(collectl_filename,'r')

    #Parse log file line-by-line
    line=collectl_log.readline()
    while len(line)>0:
        #Only parse sections headed by the specified header string
        if re.match(header_string,line):
            #If this is the first time the header has been encoutered, populate the field array
            if len(fields)==0:
                line=collectl_log.readline()
                #Store fields in order and initialise collectl_data dictionary fields
                #if line[0]=='#':
                #    line=line[1:]
                for i,field in enumerate(line.split()):
                    fields.append(field)
                    collectl_data[field]={}
                    if field==ID_fieldname:
                        ID_field=i
                #Rewind 1 line so that parsing flow is not disturbed by the initialisation just performed
                collectl_log.seek(-1,1)
            #Advance from header to first process line
            line=collectl_log.readline()
            line=collectl_log.readline()
            #Parse every line in the section.
            #Sections are normally terminated by a line with just a carriage return
            #a blank line indicates the end of file and the string 'Ouch!' is inserted if an interrupt was received by collectl
            while len(line)>1 and not re.match('Ouch!',line) and not re.match('Bogus',line):
                #Split the line into fields
                data=line.split()
                #Use the specified ID field to index the field dictionaries
                ID=data[ID_field]
                #Initialise the field dictionaries the first time each ID is encountered
                if ID not in collectl_data[fields[0]]:
                    for field in fields:
                        collectl_data[field][ID]=[]
                #Copy data from log file into dictionary as strings.
                for i,field in enumerate(fields):
                    collectl_data[field][ID].append(data[i])
                #Get next line in the section
                line=collectl_log.readline()
        #Get next line in the file (looking for the next section of interest)
        line=collectl_log.readline()
    collectl_log.close()
    #Return the data dictionary
    return collectl_data

#--------------------------------------------------------------------
# Support functions used by other functions in this library
#--------------------------------------------------------------------
# Function to remove all process data not matching (search not match) the regex "filter"
#--------------------------------------------------------------------
def filter_data(collectl_data,filter):
    for field in collectl_data.keys():
        for process in collectl_data[field].keys():
            if not re.search(filter,process):
                del collectl_data[field][process]
    return collectl_data

#--------------------------------------------------------------------
# Function for removing # character from the start of the first field name
#--------------------------------------------------------------------
def strip_hash(collectl_data):
    fields=collectl_data.keys()
    for field in fields:
        if field[0]=='#':
            collectl_data[field[1:]]=collectl_data[field]
            del collectl_data[field]
    return collectl_data

#--------------------------------------------------------------------
# Function for adding a seconds since epoch timestamp for every ID in the data dictioanry
# This is pretty slow at the moment
#--------------------------------------------------------------------
def add_seconds_since_epoch_field(collectl_data):
    #Initialise the seconds since epoch dictionary
    collectl_data["seconds_since_epoch"]={}
    #Process each ID (e.g. CPU ID or process name)
    for ID in sorted(collectl_data["Date"].keys()):
        print "Calculating seconds since epoch for",ID
        #Initialise seconds since epoch array for ID
        collectl_data["seconds_since_epoch"][ID]=zeros(len(collectl_data["Date"][ID]),dtype=float)
        i=0
        #Create an itterator from the date time pairs and itterate over it
        for d,t in izip(collectl_data["Date"][ID],collectl_data["Time"][ID]):
            #Create datetime object by parsing concatenated date and time strings
            dt=dateutil.parser.parse(d + ' ' + t)
            #Extract microseconds since epoch from timetuple (includes date with 1 second resolution) and add microseconds from time (time doesn't include date)
            collectl_data["seconds_since_epoch"][ID][i]=time.mktime(dt.timetuple())+(float(dt.time().microsecond)/1000000.0)
            i+=1
    #Return the updated data dictionary
    return collectl_data

#--------------------------------------------------------------------
# Function for removing date and time fields from the data dictionary
#--------------------------------------------------------------------
def remove_date_and_time_fields(collectl_data):
    fields=collectl_data.keys()
    for field in fields:
        if field in ('Date','Time'):
            del collectl_data[field]
    return collectl_data


#--------------------------------------------------------------------
# Functions useful for further processing the extracted data
#--------------------------------------------------------------------
# Offsets all time stamps in the "seconds_since_epoch" dictionary by -offset seconds.
# This is useful for adjusting log data to a common reference time or for accounting for time zone
#--------------------------------------------------------------------
def offset_all_seconds_since_epoch_timestamps(collectl_data,offset):
    for ID in collectl_data["seconds_since_epoch"]:
        collectl_data["seconds_since_epoch"][ID]=subtract(collectl_data["seconds_since_epoch"][ID],offset)
    return collectl_data

#--------------------------------------------------------------------
# Finds the earliest timestamp in the "seconds_since_epoch" dictionary.
# It is assumed that the timestamp arrays are in chronological order,
# which they should be as long as no clock step-adjustments occured during log generation
#--------------------------------------------------------------------
def find_start_time(collectl_data):
    start_time=collectl_data["seconds_since_epoch"][collectl_data["seconds_since_epoch"].keys()[0]][0]
    for process in collectl_data["seconds_since_epoch"]:
        if collectl_data["seconds_since_epoch"][process][0]<start_time:
            start_time=collectl_data["seconds_since_epoch"][process][0]
    return start_time


def get_collectl_plot_data_itrs(collectl_filename,date_string):
    #Open file
    collectl_log=open(collectl_filename,'r')
    header,keys=parse_collectl_itrs_header(collectl_log)

    # build up tuple for date and time to convert to seconds_since_epoch
    date=[]
    date_list=list(date_string)
    date.append(date_list[0]+date_list[1]+date_list[2]+date_list[3])
    date.append(date_list[4]+date_list[5])
    date.append(date_list[6]+date_list[7])
    date.append("00")
    date.append("00")
    date.append("00")

    #Initialise data dictionary
    cpu_data={}
    cpu_seconds_since_epoch=[]
    if header[0] == '#memTot':
        cpu_data['General Memory Stats']={}
        for key in keys:
            if key not in cpu_data['General Memory Stats']:
                cpu_data['General Memory Stats'][key]=[[],[]]
    else:
        for key in keys:
            if key not in cpu_data:
                cpu_data[key]={}

    #Parse log file line-by-line.
    line=collectl_log.readline()
    while len(line)>0:
        dataline=line.split(",")

        #get timestamp and convert to seconds since epoch
        times=dataline[-1].split(":")
        for i,value in enumerate(times):
            date[i+3]=value
        time_tuple=(int(date[0]),int(date[1]),int(date[2]),int(date[3]),int(date[4]),int(date[5]),0,0,0)
        seconds_since_epoch=time.mktime(time_tuple)

        #Skip data field
        if header[0] == '#memTot':
            for i,value in enumerate(dataline[1:-1]):
                #if dataline[0] not in cpu_data[keys[i]]:
                #    cpu_data[keys[i]][dataline[0]]=[[],[]]
                cpu_data['General Memory Stats'][keys[i]][1].append(int(value))
                cpu_data['General Memory Stats'][keys[i]][0].append(float(seconds_since_epoch))
            line=collectl_log.readline()

        #Skip data field
        if header[0] == '#CPU':
            for i,value in enumerate(dataline[1:-1]):
                if dataline[0] not in cpu_data[keys[i]]:
                    cpu_data[keys[i]][dataline[0]]=[[],[]]
                cpu_data[keys[i]][dataline[0]][1].append(int(value))
                cpu_data[keys[i]][dataline[0]][0].append(float(seconds_since_epoch))
            line=collectl_log.readline()

        if header[0] == '#netName':
            for i,value in enumerate(dataline[1:-1]):
                if dataline[0] not in cpu_data[keys[i]]:
                    cpu_data[keys[i]][dataline[0]]=[[],[]]
                cpu_data[keys[i]][dataline[0]][1].append(int(value))
                cpu_data[keys[i]][dataline[0]][0].append(float(seconds_since_epoch))
            line=collectl_log.readline()

        #Skip data field
        if header[0] == '#HCA':
            for i,value in enumerate(dataline[1:-1]):
                if dataline[0] not in cpu_data[keys[i]]:
                    cpu_data[keys[i]][dataline[0]]=[[],[]]
                cpu_data[keys[i]][dataline[0]][1].append(int(value))
                cpu_data[keys[i]][dataline[0]][0].append(float(seconds_since_epoch))
            line=collectl_log.readline()

        if header[0] == '#procCmd':
            for i,value in enumerate(dataline[1:-1]):
                if i == 1 or i == 5:
                    continue
                cmd=(dataline[0].split(" "))[0]
                if cmd not in cpu_data[keys[i]]:
                    cpu_data[keys[i]][cmd]=[[],[]]
                if i == 12:
                    #convert AccuTime to seconds
                    tempStr=value.replace(".",":")
                    accuTimeStr=tempStr.split(":")
                    accuTime = (21600 * int(accuTimeStr[0])) +\
                               (3600 * int(accuTimeStr[1]))  +\
                               (60 * int(accuTimeStr[2]))
                    cpu_data[keys[i]][cmd][1].append(int(accuTime))
                    cpu_data[keys[i]][cmd][0].append(float(seconds_since_epoch))
                    continue

    #Close file
    collectl_log.close()
    return cpu_data

def get_collectl_plot_data_cpu(collectl_filename,ID_fieldname,header_string):
    #Open file
    collectl_log=open(collectl_filename,'r')

    #Skip generic header, do this in a function so parsing can be changed in just one place
    parse_collectl_generic_header(collectl_log)

    #Get cpu specific header
    keys=parse_collectl_cpu_header(collectl_log)

    #Initialise data dictionary
    cpu_data={}
    cpu_seconds_since_epoch=[]
    for key in keys:
        if key[0] not in cpu_data:
            cpu_data[key[0]]={}
        cpu_data[key[0]][key[1]]=[]
    seconds_since_epoch=[]
    #Parse log file line-by-line. Not sure if it is worth casting here, might be better to do it later when casting to numpy arrays
    line=collectl_log.readline()
    while len(line)>0:
        dataline=line.split()
        seconds_since_epoch.append(float(dataline[0]))
        #Skip data field
        for i,value in enumerate(dataline[1:]):
            cpu_data[keys[i][0]][keys[i][1]].append(int(value))
        line=collectl_log.readline()

    #Cast everything to numpy arrays and add times
    seconds_since_epoch=array(seconds_since_epoch,dtype=int)
    for key in keys:
        cpu_data[key[0]][key[1]]=array([seconds_since_epoch,cpu_data[key[0]][key[1]]])

    #Close file
    collectl_log.close()
    return cpu_data

def get_collectl_plot_data_network(collectl_filename,ID_fieldname,header_string):
    #Open file
    collectl_log=open(collectl_filename,'r')

    #Skip generic header, do this in a function so parsing can be changed in just one place
    parse_collectl_generic_header(collectl_log)

    #Get cpu specific header
    keys=parse_collectl_network_header(collectl_log)

    #Initialise data dictionary
    network_data={}
    seconds_since_epoch=[]
    for key in keys:

        if key[0] not in network_data and key[0]!='Name':
            network_data[key[0]]={}
        if key[0]!='Name' and key[1] not in network_data[key[0]] :
            network_data[key[0]][key[1]]=[]

    #Parse log file line-by-line. Not sure if it is worth casting here, might be better to do it later when casting to numpy arrays
    line=collectl_log.readline()
    while len(line)>0:
        dataline=line.split()
        seconds_since_epoch.append(float(dataline[0]))
        #Skip date field
        for i,value in enumerate(dataline[1:]):
            if keys[i][0]!='Name':
                network_data[keys[i][0]][keys[i][1]].append(int(value))
        line=collectl_log.readline()
    #Cast everything to numpy arrays and add times
    seconds_since_epoch=array(seconds_since_epoch,dtype=int)
    for key in keys:
        if key[0]!='Name':
            network_data[key[0]][key[1]]=array([seconds_since_epoch,network_data[key[0]][key[1]]])
    #Close file
    collectl_log.close()
    return network_data

def get_collectl_plot_data_process(collectl_filename,start_time,head,duration):
    #Open file
    collectl_log=open(collectl_filename,'r')

    #Skip generic header, do this in a function so parsing can be changed in just one place
    parse_collectl_generic_header(collectl_log)

    #Get cpu specific header
    headers=parse_collectl_get_header(collectl_log)

    #Not used
    #non_numeric_keys=['User','PR','Time','S','AccuTime','Command']
    int_keys=['Pct','PCT',   'THRD', 'PID',   'CP', 'PPID','CPU','RSYS','WSYS','CNCL' ]
    float_keys=['SysT', 'UsrT']
    scaled_numeric_keys=['VmSize','VmLck','VmRSS','VmData','VmStk','VmExe','VmLib','MajF','MinF','WKB','RKB','WKBC','RKBC']
    scalers={'K':1000,'M':1000000,'G':1000000000,'T':1000000000000}

    #Initialise data dictionary
    process_data={}
    for header in headers[:-1]:
        if header in int_keys or header in float_keys or header in scaled_numeric_keys:
            process_data[header]={}

    line=collectl_log.readline()
    while len(line)>0 and not re.match('#|Ouch',line):
        dataline=line.split()
        seconds_since_epoch=float(dataline[0])
        if start_time==-1:
            start_time=seconds_since_epoch
            print "head:",head
            print "duration:",duration
            print "starting at:",str(head+start_time)
            print "ending at:",str(start_time+head+duration)

        #this was used when data was not plotted aginst date
        #seconds_since_epoch-=start_time
        command=str(dataline[1]) + " "
        #print seconds_since_epoch
        if seconds_since_epoch>=(head+start_time) and seconds_since_epoch<=(start_time+head+duration):
            #print "."
            for section in dataline[len(headers):]:
                command+=' '+ section
            for i,header in enumerate(headers[:-1]):
                if header in int_keys:
                    if command not in process_data[header]:
                        process_data[header][command]=[[],[]]
                    process_data[header][command][0].append(seconds_since_epoch)
                    process_data[header][command][1].append(int(dataline[i+1]))
                if header in float_keys:
                    if command not in process_data[header]:
                        process_data[header][command]=[[],[]]
                    process_data[header][command][0].append(seconds_since_epoch)
                    process_data[header][command][1].append(float(dataline[i+1]))
                elif header in scaled_numeric_keys:
                    #print dataline[i+1][-1]
                    if command not in process_data[header]:
                        process_data[header][command]=[[],[]]
                    process_data[header][command][0].append(seconds_since_epoch)
                    if dataline[i+1][-1] in scalers:
                        #print scalers[dataline[i+1][-1]]
                        process_data[header][command][1].append(int(dataline[i+1][:-1])*scalers[dataline[i+1][-1]])
                    else:
                        process_data[header][command][1].append(int(dataline[i+1]))

        line=collectl_log.readline()
    #Cast everything to numpy arrays, assume that there is no need to cast data type
    for key in process_data.keys():
        for process in process_data[key]:
            process_data[key][process][0]=array(process_data[key][process][0])
            process_data[key][process][1]=array(process_data[key][process][1])
    #Close file
    collectl_log.close()
    return process_data

def parse_collectl_generic_header(collectl_log):
    line=collectl_log.readline()

    if re.match('##',line):
        #Start of header found
        line=collectl_log.readline()
        while not re.match('##',line) and len(line)>0:
            line=collectl_log.readline()
        if len(line)==0:
            print 'Error, collectl log appears to be truncated in the middle of the header'
            exit()
    else:
        #print 'Error, collectl log does not start with the expected header line'
        #exit()
        pass
    return

def parse_collectl_itrs_header(collectl_log):
    headers=(collectl_log.readline().strip("\n")).split(",")
    allowed_headers=['#CPU','#netName','#procCmd','#HCA','#memTot']
    if headers[0] not in allowed_headers:
        print 'Error, collectl itrs log header not recognised: ',headers[0]
        print "Expected: ",allowed_headers
        exit()
    keys=[]
    for header in headers[1:-1]:
        keys.append(header.strip("\n"))
    return headers, keys

def parse_collectl_cpu_header(collectl_log):
    headers = parse_collectl_get_header(collectl_log)
    keys=[]
    cpus=0
    for header in headers:
        matches=re.search('\[CPU:([0-9]+)\]([A-Za-z].*)',header).groups()
        keys.append((matches[1],matches[0]))
    return keys


def parse_collectl_network_header(collectl_log):
    headers=collectl_log.readline().split()
    if headers[0]!='#UTC':
        print 'Error, collectl log network header not recognised'
        exit()
    keys=[]
    cpus=0
    for header in headers[1:]:
        matches=re.search('\[NET:(.*)\]([A-Za-z].*)',header).groups()
        keys.append((matches[1],matches[0]))
    return keys

def parse_collectl_get_header(collectl_log):
    line=collectl_log.readline()
    while len(line)>0:
        headers=line.split()
        if headers[0]=='#UTC':
            keys=[]
            cpus=0
            for header in headers[1:]:
                keys.append(header)
            return keys
        line=collectl_log.readline()

    print 'Error, collectl log process header not recognised'
    exit()



