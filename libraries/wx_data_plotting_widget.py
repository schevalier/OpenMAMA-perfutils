import wx
import numpy
import  wx.lib.scrolledpanel as scrolled
import matplotlib.figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas, NavigationToolbar2WxAgg as NavigationToolbar
import pylab
import os
import sys
import re
import datetime

class GraphFrame(wx.Frame):
    """ The main frame of the application """

    def __init__(self,data,frametitle,graphtitle,x_label,y_label,imgfilename="",imgtitle=""):    #imgfilename and imgtitle are optional
        wx.Frame.__init__(self, None, -1, frametitle)

        self.data = data

        self.graphtitle = graphtitle
        self.x_label = x_label
        self.y_label = y_label

        self.line_style=['None']
        self.markers=['D','s','*','^']

        self.legend=True
        self.x_format='Date'
        self.normalise=False
        # check for bitmap image filename
        if imgfilename == "" and imgtitle == "":
            self.has_image = False
        else:
            self.has_image = True
            self.imgfilename = imgfilename
            self.imgtitle = imgtitle

        self.create_menu()
        self.create_status_bar()
        self.create_main_panels()


    def create_menu(self):
        self.menubar = wx.MenuBar()

        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)


    def create_main_panels(self):
        #Create panels
        self.graph_panel = wx.Panel(self)
        self.checkbox_panel = scrolled.ScrolledPanel(self)

        #Create buttons, text controls and labels
        self.ResetButton=wx.Button(self.graph_panel,1,'Fit Axes',size=(150,20))
        self.StyleButton=wx.Button(self.graph_panel,2,'Toggle Plot Style',size=(150,20))
        self.NormaliseButton=wx.Button(self.graph_panel,5,'Normalise Plot',size=(150,20))
        self.ClearButton=wx.Button(self.graph_panel,6,'Clear Plot',size=(150,20))
        self.LegendButton=wx.Button(self.graph_panel,7,'Toggle Legend',size=(150,20))
        self.CSVButton=wx.Button(self.graph_panel,8,'CSV',size=(150,20))
        self.CheckButton=wx.Button(self.graph_panel,10,'Select Regex',size=(150,20))
        self.DateButton=wx.Button(self.graph_panel,11,'Toggle Date Format',size=(150,20))

        self.title_label=wx.StaticText(self.graph_panel,label='Plot Title')
        self.title_ctrl=wx.TextCtrl(self.graph_panel,12,style=wx.TE_PROCESS_ENTER)
        self.x_label_label=wx.StaticText(self.graph_panel,label='X Axis Label')
        self.x_label_ctrl=wx.TextCtrl(self.graph_panel,3,style=wx.TE_PROCESS_ENTER)
        self.y_label_label=wx.StaticText(self.graph_panel,label='Y Axis Label')
        self.y_label_ctrl=wx.TextCtrl(self.graph_panel,4,style=wx.TE_PROCESS_ENTER)
        self.CSV_output_label=wx.StaticText(self.graph_panel,label='CSV Output')
        self.CSV_output_ctrl=wx.TextCtrl(self.graph_panel,9,style=wx.TE_PROCESS_ENTER)
        self.Checkboxes_label=wx.StaticText(self.graph_panel,label='Regex')
        self.Checkboxes_ctrl=wx.TextCtrl(self.graph_panel,11,style=wx.TE_PROCESS_ENTER)

        #Register events
        self.Bind(wx.EVT_BUTTON,self.reset_axes,id=1)
        self.Bind(wx.EVT_BUTTON,self.toggle_plot_style,id=2)
        self.Bind(wx.EVT_TEXT_ENTER,self.set_xlabel,id=3)
        self.Bind(wx.EVT_TEXT_ENTER,self.set_ylabel,id=4)
        self.Bind(wx.EVT_BUTTON,self.toggle_normalise_plot,id=5)
        self.Bind(wx.EVT_BUTTON,self.clear_plot,id=6)
        self.Bind(wx.EVT_BUTTON,self.toggle_legend,id=7)
        self.Bind(wx.EVT_BUTTON,self.get_csv,id=8)
        self.Bind(wx.EVT_BUTTON,self.checker,id=10)
        self.Bind(wx.EVT_BUTTON,self.toggle_date_format,id=11)
        self.Bind(wx.EVT_TEXT_ENTER,self.set_plot_title,id=12)

        self.init_plots()
        self.canvas = FigCanvas(self.graph_panel, -1, self.fig)
        self.canvas.mpl_connect('motion_notify_event', self.update_status_bar)
        self.navtoolbar = NavigationToolbar(self.canvas)
        self.checkboxes = []
        self.checkboxtitles = []

        #for each key, i.e. "1. A_CheckListBox", create a checklistbox and corresponding title
        for key in sorted(self.data.keys()):
            self.checkboxes.append(wx.CheckListBox(self.checkbox_panel, 0, wx.DefaultPosition, (180,110), sorted(self.data[key].keys())))
            self.checkboxtitles.append(wx.StaticText(self.checkbox_panel, -1, key, style=wx.ALIGN_LEFT))

        self.left_panel_main_vbox = wx.BoxSizer(wx.VERTICAL)
        self.left_panel_main_vbox.Add(self.canvas, proportion=1,border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.GROW)
        self.left_panel_main_vbox.AddSpacer(20)

        self.left_panel_controls_vbox = wx.BoxSizer(wx.VERTICAL)


        self.left_panel_buttons_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.left_panel_buttons_hbox_2 = wx.BoxSizer(wx.HORIZONTAL)

        self.left_panel_buttons_hbox.Add(self.StyleButton, border=5)
        self.left_panel_buttons_hbox.Add(self.CSVButton, border=5, flag=wx.EXPAND)
        self.left_panel_buttons_hbox.Add(self.NormaliseButton, border=5)
        self.left_panel_buttons_hbox.Add(self.ClearButton, border=5)

        self.left_panel_buttons_hbox_2.Add(self.DateButton, border=5)
        self.left_panel_buttons_hbox_2.Add(self.LegendButton, border=5)
        self.left_panel_buttons_hbox_2.Add(self.CheckButton, border=5)
        self.left_panel_buttons_hbox_2.Add(self.ResetButton, border=5)


        self.left_panel_labels_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.left_panel_labels_hbox_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.left_panel_labels_hbox.Add(self.title_label,proportion=0)
        self.left_panel_labels_hbox.AddSpacer(21)
        self.left_panel_labels_hbox.Add(self.title_ctrl,proportion=0)
        self.left_panel_labels_hbox.Add(self.CSV_output_label,proportion=0)
        self.left_panel_labels_hbox.AddSpacer(4)
        self.left_panel_labels_hbox.Add(self.CSV_output_ctrl,proportion=0)
        self.left_panel_labels_hbox_2.Add(self.x_label_label,proportion=0)
        self.left_panel_labels_hbox_2.Add(self.x_label_ctrl,proportion=0)
        self.left_panel_labels_hbox_2.Add(self.y_label_label,proportion=0)
        self.left_panel_labels_hbox_2.Add(self.y_label_ctrl,proportion=0)
        self.left_panel_labels_hbox_2.Add(self.Checkboxes_label,proportion=0)
        self.left_panel_labels_hbox_2.Add(self.Checkboxes_ctrl,proportion=0)

        self.left_panel_controls_vbox.Add(self.left_panel_buttons_hbox,proportion=0)
        self.left_panel_controls_vbox.Add(self.left_panel_buttons_hbox_2,proportion=0)
        self.left_panel_controls_vbox.AddSpacer(5)
        self.left_panel_controls_vbox.Add(self.left_panel_labels_hbox,proportion=0)
        self.left_panel_controls_vbox.Add(self.left_panel_labels_hbox_2,proportion=0)

        self.left_panel_main_vbox.Add(self.left_panel_controls_vbox,proportion=0)
        self.left_panel_main_vbox.AddSpacer(10)
        self.left_panel_main_vbox.Add(self.navtoolbar,proportion=0,border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)


        #create vertical box to hold all the checklistboxes
        self.right_panel_main_vbox = wx.BoxSizer(wx.VERTICAL)
        for i in range(0,len(self.checkboxes)):
            #add each checklistbox and title to the vertical box, and bind a checklistbox event to each checklistbox
            self.right_panel_main_vbox.Add(self.checkboxtitles[i], proportion=0,border=5, flag=wx.ALL | wx.GROW)
            self.right_panel_main_vbox.Add(self.checkboxes[i], proportion=1,border=5, flag=wx.ALL | wx.GROW)
            self.Bind(wx.EVT_CHECKLISTBOX, self.on_checked_box, self.checkboxes[i])

        #if there is an image, create a bitmap and add it to the bottom of the vertical box
        if self.has_image:
            self.bmap = wx.Bitmap(self.imgfilename)
            self.diagram = wx.StaticBitmap(self.checkbox_panel, wx.ID_ANY, self.bmap)
            imgtext = wx.StaticText(self.checkbox_panel, -1, self.imgtitle, style=wx.ALIGN_CENTER)
            self.right_panel_main_vbox.Add(imgtext, proportion=0, border=5, flag=wx.ALL | wx.GROW)
            self.right_panel_main_vbox.Add(self.diagram, proportion=0, border=5, flag=wx.ALL | wx.ALIGN_CENTER)

        self.frame_hbox = wx.BoxSizer(wx.HORIZONTAL)
        #self.frame_hbox.Add(self.left_panel_main_vbox, proportion=3, border=5, flag=wx.ALL | wx.ALIGN_LEFT | wx.GROW)
        #self.frame_hbox.Add(self.right_panel_main_vbox, proportion=1, border=5, flag=wx.ALL | wx.ALIGN_RIGHT | wx.GROW)
        self.left_panel_main_vbox.Fit(self)
        self.right_panel_main_vbox.Fit(self)


        self.graph_panel.SetSizer(self.left_panel_main_vbox)
        self.graph_panel.SetAutoLayout(1)

        self.checkbox_panel.SetSizer(self.right_panel_main_vbox)
        self.checkbox_panel.SetAutoLayout(1)
        self.checkbox_panel.SetupScrolling()

        self.frame_hbox.Add(self.graph_panel,1,wx.EXPAND | wx.ALL,3)
        self.frame_hbox.Add(self.checkbox_panel,1,wx.EXPAND | wx.ALL,3)
        self.frame_hbox.Fit(self)

        self.SetSizer(self.frame_hbox)

        self.draw_plot()

    def set_plot_title(self,event):
        self.graphtitle=self.title_ctrl.GetValue()
        self.draw_plot()

    def set_xlabel(self,event):
        self.x_label=self.x_label_ctrl.GetValue()
        self.draw_plot()

    def set_ylabel(self,event):
        self.y_label=self.y_label_ctrl.GetValue()
        self.draw_plot()

    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()


    def init_plots(self):
        self.dpi = 100
        self.fig = matplotlib.figure.Figure((3.0, 3.0), dpi=self.dpi)
        self.plot_range=[0,1,0,1]
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(True)
        box = self.axes.get_position()
        self.axes.set_position([box.x0, box.y0+0.2*box.height, box.width , box.height* 0.8])

    def init_axes(self,title):
    	#self.axes.clear()
        self.axes.set_title(title, size=12)
        self.axes.get_yaxis().set_label_text(self.y_label)
        self.axes.get_xaxis().set_label_text(self.x_label)
        #self.axes.autoscale(enable=False,axis='both')
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)
        if self.x_format=='Date':
            self.axes.xaxis_date()
            #self.axes.get_xaxis().set_major_locator(matplotlib.ticker.MaxNLocator(4))
            #self.axes.get_xaxis().set_minor_locator(matplotlib.ticker.MaxNLocator(1))
            hfmt = matplotlib.dates.DateFormatter('%d/%m/%y %H:%M:%S')
            self.axes.get_xaxis().set_major_locator(matplotlib.dates.AutoDateLocator())
            self.axes.get_xaxis().set_major_formatter(hfmt)
            labels = self.axes.get_xticklabels()
            for label in labels:
                label.set_rotation('vertical')
        else:
            pass

    def on_checked_box(self,event):
        self.draw_plot()

    def draw_plot(self):
    	self.axes.clear()

        keys=sorted(self.data.keys())
        colors=['b','g','r','c','m','y','k']
        num_colors=len(colors)
        linestyles=self.line_style
        num_linestyles=len(linestyles)
        markers=self.markers
        num_markers=len(markers)
        num_plots=0
        xmin=sys.maxint
        ymin=sys.maxint
        xmax=-sys.maxint
        ymax=-sys.maxint
        #for each key i.e. "1. A_CheckListBox"
        for i,key in enumerate(sorted(self.data.keys())):
            #get the sorted keys i.e. "A_CheckListBox_item_1","A_CheckListBox_item_2"
            keys=sorted(self.data[key].keys())
            #for each checked box in each checklistbox
            for id in sorted(self.checkboxes[i].Checked):
                num_plots+=1
                xdata=self.data[key][keys[id]][0]

                if self.x_format=='Date':
                    #xdata=self.data[key][keys[id]][0]
                    dts = map(datetime.datetime.fromtimestamp, xdata)
                    xdata = matplotlib.dates.date2num(dts)


                #plot each set of data points that correspond to each checked box
                if self.normalise:
                    ydata=numpy.array(self.data[key][keys[id]][1],dtype='float')
                    normalisation_factor=float(max(ydata))
                    ydata=numpy.divide(ydata,normalisation_factor)

                    if normalisation_factor==0:
                        normalisation_factor=1
                    self.axes.plot( xdata,
                                ydata,
                                marker=markers[(int(i+id/num_colors))%num_markers],
                                markersize=4,
                                mec=colors[(i+id)%num_colors],
                                linestyle=linestyles[int(int(i+id/num_colors)/num_markers)%num_linestyles],
                                color=colors[(i+id)%num_colors],
                                label=key + " " + sorted(self.data[key].keys())[id])
                else:
                    ydata=numpy.array(self.data[key][keys[id]][1],dtype='float')

                    self.axes.plot( xdata,
                                ydata,
                                marker=markers[(int(i+id/num_colors))%num_markers],
                                markersize=4,
                                mec=colors[(i+id)%num_colors],
                                linestyle=linestyles[int(int(i+id/num_colors)/num_markers)%num_linestyles],
                                color=colors[(i+id)%num_colors],
                                label=key + " " + sorted(self.data[key].keys())[id])

                xmin_cur=min(xdata)
                xmax_cur=max(xdata)
                ymin_cur=min(ydata)
                ymax_cur=max(ydata)

                if xmin_cur<xmin:
                    xmin=xmin_cur
                if xmax_cur>xmax:
                    xmax=xmax_cur
                if ymin_cur<ymin:
                    ymin=ymin_cur
                if ymax_cur>ymax:
                    ymax=ymax_cur

        if num_plots>0:
            self.plot_range=[xmin,xmax,ymin,ymax]
        else:
            self.plot_range=[0,1,0,1]
        self.axes.axis(self.plot_range)

        if num_plots>0 and self.legend:
            self.axes.legend(loc='upper right')
        self.init_axes(self.graphtitle)

        self.canvas.draw()

    def toggle_legend(self,event):
        self.legend=not self.legend
        self.draw_plot()

    def checker(self,event):
    	tocheck=self.Checkboxes_ctrl.GetValue()
    	for i,item in enumerate(self.checkboxes):
    	    for id,key in enumerate(item.GetStrings()):
    			if re.search(tocheck, key):
    				self.checkboxes[i].Check(id,True)
    	self.draw_plot()

    def get_csv(self,event):
		filename=self.CSV_output_ctrl.GetValue()
		if len(filename)==0:
		    filename="output.csv"
		    print "NO OUTPUT SPECIFIED! DEFAULTING TO ",filename
		output=open(filename,'w')
		pdict={}
		for i,key in enumerate(sorted(self.data.keys())):
			keys=sorted(self.data[key].keys())
			for id in sorted(self.checkboxes[i].Checked):
				newkey2=str(i)+str(keys[id])
				newkey=str(key)+"_"+str(keys[id])
				pdict[newkey]=self.data[key][keys[id]]
		pkeys=pdict.keys()
		plength=[]
		if len(pkeys)==0:
		    print "NO CHECKBOXES ARE CHECKED; ",filename, "will be created empty."
		    return 1

		for pkey in pkeys:
			plength.append(len(pdict[pkey][0]))
			sindices=[]
			sindices=sorted(range(len(plength)),reverse=True,key=lambda x:plength[x])
			pcols=len(sindices)
		print "WRITING..."
		for index in sindices:
			output.write(pkeys[index])
			output.write("_x")
			output.write(",")
			output.write(pkeys[index])
			output.write("_y")
			output.write(",")
		output.write('\n')

		for row in range(plength[sindices[0]]):
			for col in range(len(sindices)):
				if len(pdict[pkeys[sindices[col]]][0]) > row:
					output.write(str(pdict[pkeys[sindices[col]]][0][row]))
					output.write(",")
					output.write(str(pdict[pkeys[sindices[col]]][1][row]))
					output.write(",")
			output.write( '\n' )
		print"DONE!"


    def toggle_date_format(self,event):
        if self.x_format=='Date':
            self.x_format='Number'
        else:
            self.x_format='Date'
        self.draw_plot()

    def reset_axes(self,event):
        #self.axes.autoscale(enable=True,axis='both')
        self.draw_plot()
        #self.axes.autoscale(enable=False,axis='both')


    def toggle_plot_style(self,event):
        if 'None' in self.line_style:
            self.line_style=['-','--',':']
            self.markers=['None']
        else:
            self.line_style=['None']
            self.markers=['D','s','*','^']
        self.draw_plot()

    def toggle_normalise_plot(self,event):
        self.normalise=not self.normalise
        self.reset_axes(event)

    def clear_plot(self,event):
        for checkboxlist in self.checkboxes:
            for index in checkboxlist.Checked:
                checkboxlist.Check(index,False)
        self.reset_axes(event)
        self.draw_plot()

    def scale_axes(self,axes):
        cur_range=axes.axis()
        if cur_range[0]<self.plot_range[0]:
            self.plot_range[0]=cur_range[0]
        if cur_range[1]>self.plot_range[1]:
            self.plot_range[1]=cur_range[1]
        if cur_range[2]<self.plot_range[2]:
            self.plot_range[2]=cur_range[2]
        if cur_range[3]>self.plot_range[3]:
            self.plot_range[3]=cur_range[3]
        axes.axis(self.plot_range)


    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"

        dlg = wx.FileDialog(
        self,
        message="Save plot as...",
        defaultDir=os.getcwd(),
        defaultFile="plot.png",
        wildcard=file_choices,
        style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)


    def on_exit(self, event):
        self.Destroy()


    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
                    wx.EVT_TIMER,
                    self.on_flash_status_off,
                    self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)


    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

    def update_status_bar(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.statusbar.SetStatusText(( "x= " + str(x) + "  y=" +str(y) ), 0)
