#!/usr/bin/python
from sys import maxint
from optparse import OptionParser
import dateutil
import time
#from pylab import show, figure
import numpy
import re
from data_plotting_functions import save_image, plot_stats
import data_file_processing_functions
import matplotlib
matplotlib.use('WXAgg')
import numpy as np
import wx
import wx_data_plotting_widget
import collectlParserlib


#--------------------------------------------------------------------
# Main
#--------------------------------------------------------------------

cpufreq=1
proc_filter='./'
plot_show=False
data={}

parser = OptionParser("usage: %prog [options] filename")
# behaviour options
parser.add_option("-G","--gui",     action="store_true", default=False,                     dest="show_gui",    help="Show [G]UI interface for data.")
parser.add_option("-S","--save",    action="store",                          type="string", dest="savename",    help="Filename to [S]ave processed data dictionary to")
parser.add_option("-L","--load",    action="store",                          type="string", dest="loadname",    help="Filename to [L]oad processed data dictionary from")
# MAMA file processing
parser.add_option("-P","--pub",     action="store",                          type="string", dest="publog",      help="File name of [P]ublisher log")
parser.add_option("-C","--cons",    action="store",                          type="string", dest="conslog",     help="File name of [C]onsumer log")
parser.add_option("-t","--total",   action="store_true", default=False,                     dest="total",       help="Calculate [T]otal statistics for publishers")
parser.add_option("-F","--freq",    action="store",                          type="int",    dest="cpufreq",     help="Scale consumer stats by cpu [F]requency.")
# CollectL file parsing
parser.add_option("-c","--cpulog",  action="store",                          type="string", dest="cpulog",      help="File name of collectl [C]pu log")
parser.add_option("-n","--netlog",  action="store",                          type="string", dest="netlog",      help="File name of collectl [N]etwork log")
parser.add_option("-z","--prclog",  action="store",                          type="string", dest="prclog",      help="File name of collectl process log (-s[Z])")
parser.add_option("-x","--iblog",   action="store",                          type="string", dest="iblog",       help="File name of collectl infiniband log (-s[X])")
parser.add_option("-m","--memlog",  action="store",                          type="string", dest="memlog",      help="File name of collectl [M]emory log")
# Netstat
parser.add_option("-N","--netstat", action="store",                          type="string", dest="netstatlog",  help="File name of [n]etstat log")

(options, args) = parser.parse_args()

if options.cpufreq is not None:
    cpufreq = options.cpufreq

if options.loadname is not None:
    try:
        data_archive=numpy.load(options.loadname)
    except:
        print 'Data archive could not be loaded'
        exit(0)
    for key in data_archive.keys():
        data[key]=data_archive[key][()]

# Parse producer logs
if options.publog is not None:
    data.update(data_file_processing_functions.process_mamaproducer_logs(options.publog, './'))

# Parse consumer logs
if options.conslog is not None:
    data.update(data_file_processing_functions.process_mamaconsumer_logs(options.conslog, './',cpufreq))

# Parse collectl logs
if options.cpulog is not None:
    print "processing ",options.cpulog," ..."
    data.update(collectlParserlib.get_collectl_plot_data_cpu(options.cpulog,"CPU",""))

if options.netlog is not None:
    print "processing ",options.netlog," ..."
    data.update(collectlParserlib.get_collectl_plot_data_process(options.netlog,-1,0,(10*60*60)))

if options.prclog is not None:
    print "processing ",options.prclog," ..."
    data.update(collectlParserlib.get_collectl_plot_data_process(options.prclog,-1,0,(10*60*60)))

if options.iblog is not None:
    print "processing ",options.iblog," ..."
    data.update(collectlParserlib.get_collectl_plot_data_process(options.iblog,-1,0,(10*60*60)))

if options.memlog is not None:
    print "processing ",options.memlog," ..."
    data.update(collectlParserlib.get_collectl_plot_data_process(options.memlog,-1,0,(10*60*60)))

# Parse netstat log
if options.netstatlog is not None:
    data.update(data_file_processing_functions.process_netstat_logs(options.netstatlog, './'))

# Calculate Total Stats for mamaproducers
if options.total and options.publog is not None:
    pub_keys=[]
    data['TOTAL_PUBLISHING']={}
    data['TOTAL_PUBLISHING']['RATE']=[[],[]]

    print "calculating totals..."
    for key in data.keys():
        if re.search(options.publog,key):
            pub_keys.append(key)
    for i,key in enumerate(sorted(pub_keys)):
        if i == 0:
            min_len=len(data[key]['RATE'][0])
            data['TOTAL_PUBLISHING']['RATE'][0] = map(float,data[key]['RATE'][0])
            data['TOTAL_PUBLISHING']['RATE'][1] = map(float,data[key]['RATE'][1])
        else:
            offset=len(data[key]['RATE'][0]) - min_len
            for i,rate in enumerate(data[key]['RATE'][1]):
                data['TOTAL_PUBLISHING']['RATE'][1][i-offset] += float(data[key]['RATE'][1][i])



# Check that there is something to display.
if len(data.keys())<1:
    parser.error("No data specified, specify input or use -L to load archive")
    exit()

######################################################################
#  Save parsed data
######################################################################
if options.savename is not None:
    numpy.savez(options.savename,**data)

#########################################################
# Draw Plot
#########################################################
if options.show_gui:
    app = wx.App(False)
    app.frame = wx_data_plotting_widget.GraphFrame(data,  'Graph Frame Title', 'Graph Title', 'X Axis Label', 'Y Axis Label')
    app.frame.Show()
    app.MainLoop()

