#!/usr/bin/env python
#_______________________________________________________________________
# Python functions to parse ptpd2 log files recorded with ./ptpd -g -f ptpd2_filename

#-------------------------------------------------------------------- 
# Module imports
#--------------------------------------------------------------------
import re
import itertools
#-------------------------------------------------------------------- 
# ptpd2 Log parser
#-------------------------------------------------------------------- 
def get_ptpd2_data(ptpd2_filename):
    print 'Parsing ptpd2 log file: ' + ptpd2_filename
    ptpd2_log=open(ptpd2_filename,'r')
    ptpd2_data={}
    fields=[]
    num_fields=0
    for line in ptpd2_log:
        if re.match('#',line):
            raw_fields=re.split(',',line)
            for field in raw_fields:
                fields.append(field.strip())
                ptpd2_data[field.strip()]=[]
            num_fields=len(fields)
        else:
            data=re.split(',',line)
            if num_fields==len(data):
                for field,value in itertools.izip(fields,data):
                    ptpd2_data[field].append(value)
    ptpd2_log.close()
    return ptpd2_data
