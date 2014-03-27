import numpy as np
from matplotlib import cm
from sys import exit

#--------------------------------------------------------------------
#Calculate 10% lose axis limits for data set that may or may not cross 0
#--------------------------------------------------------------------
def get_loose_axis_lims(delta_diff):
    ax_min=min(delta_diff)
    if ax_min<0:
        ax_min*=1.1
    else:
        ax_min*=0.9
    ax_max=max(delta_diff)
    if ax_max>0:
        ax_max*=1.1
    else:
        ax_max*=0.9
    return ax_min, ax_max

#--------------------------------------------------------------------
#2D Hexplotting - Seems to be better than imshow and pcolor due to mincnt parameter and surf due to speed
#xbinsize is approximate size of x bins in milliseconds
#ybinsuze is approximate size of y bins in microseconds
#NOTE:2D Square Histogram function below uses masked arrays to implement mincnt and is therefore just as good
#--------------------------------------------------------------------
def plot_hex_hist(fig,ax,match_times,delta_diff,xbinsize,ybinsize,clevels):

    #Calculate number of bins
    xbins=int(1000*max(match_times)/xbinsize)
    ybins=np.around((max(delta_diff)-min(delta_diff))/(1+ybinsize),decimals=-1)

    if (xbins*ybins) > 2000000 :
        print "Increasing bin size to reduce memory demand (2,000,000 bins max)"
        scale_factor=np.sqrt(2000000.0/float(xbins*ybins))
        xbins=int(scale_factor*xbins)
        ybins=int(scale_factor*ybins)


    #Adjust colormap to desired number of levels
    j2=cmap_discretize(cm.jet, clevels)

    #Plot hexbin
    cax=ax.hexbin(match_times,delta_diff,C=None, gridsize=(xbins,ybins),mincnt=1,cmap=j2)

    #Calculate colorbar labels and add colorbar to figure
    tick_max=int(max(np.around(cax.get_array(),decimals=-1)))
    ticks = np.array(np.linspace(0,tick_max,clevels+1),int)
    #cbar=fig.colorbar(cax,ticks=ticks)

    #Scale axes (tight for x, 10% loose for y)
    ax_min,ax_max=get_loose_axis_lims(delta_diff)
    ax.axis([match_times[0],match_times[-1],ax_min,ax_max])

#--------------------------------------------------------------------
#2D Square Histogram
#Match times are expected in seconds
#xbinsize is approximate size of x bins in milliseconds
#ybinsuze is approximate size of y bins in microseconds
#--------------------------------------------------------------------
def plot_quad_hist(fig,ax,match_times,delta_diff,xbinsize,ybinsize,clevels,colourbar=True):
    #Calculate number of bins
    xbins=int(1000*max(match_times)/xbinsize)
    ybins=np.around((max(delta_diff)-min(delta_diff))/ybinsize,decimals=-1)

    #print xbins*ybins,"bins required for specified resolution."
    if (xbins*ybins) > 10000000 :
        print "Increasing bin size to reduce memory demand (10,000,000 bins max)"
        #scale_factor=np.sqrt(10000000.0/float(xbins*ybins))
        #xbins=int(scale_factor*xbins)
        ybins=int(10000000/xbins)

    #Calculate histogram data
    H,xedges,yedges=np.histogram2d(match_times,delta_diff,bins=[xbins,ybins])
    extent = [xedges[0],xedges[-1],yedges[0],yedges[-1]]


    #Adjust colormap to desired number of levels
    j2=cmap_discretize(cm.jet, clevels)

    #Mask empty bins
    masked_data=np.transpose(np.ma.masked_equal(H,0.0))
    j2.set_bad('w',0)


    cax=ax.imshow(masked_data,extent=extent,interpolation='nearest',origin='lower',aspect='auto',cmap=j2)
    #Calculate colorbar labels and add colorbar to figure
    tick_max=int(np.max(np.around(H,decimals=-1)))
    ticks = np.array(np.linspace(0,tick_max,clevels+1),int)
    if colourbar is True:
        cbar=fig.colorbar(cax,ticks=ticks)

#--------------------------------------------------------------------
#This function is based on the one from http:/www.scipy.org/Cookbook/Matplotlib/ColormapTransformations
#It creates a colormap with N levels based on an existing colormap cmap
#The scipy interpolate call has been replace by a numpy one to remove the dependence on scipy
#--------------------------------------------------------------------
def cmap_discretize(cmap, N):
    """Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet.
        N: Number of colors.

        Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)
        """

    cdict = cmap._segmentdata.copy()
    # N colors
    colors_i = np.linspace(0,1.,N)
    # N+1 indices
    indices = np.linspace(0,1.,N+1)
    for key in ('red','green','blue'):
        # Find the N colors
        D = np.array(cdict[key])
        colors = np.interp(colors_i,D[:,0], D[:,1])
        #colors = I(colors_i)
        # Place these colors at the correct indices.
        A = np.zeros((N+1,3), float)
        A[:,0] = indices
        A[1:,1] = colors
        A[:-1,2] = colors
        # Create a tuple for the dictionary.
        L = []
        for l in A:
            L.append(tuple(l))
        cdict[key] = tuple(L)
    # Return colormap object.
    return cm.colors.LinearSegmentedColormap('colormap',cdict,1024)

#--------------------------------------------------------------------
#Draws a stats panel on the axis it is given
#--------------------------------------------------------------------
def plot_stats(ax,stats,percentiles,label):
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    ax.annotate(label, xy=(0.02,0.9), xytext=(0.02,0.9),fontsize=16)
    print_subplot(ax,'Delta Percentiles',0.02,0.35)
    print_subplot(ax,'99th %: ' + str(round(percentiles[98],1)),0.02,0.25)
    print_subplot(ax,'95th %: ' + str(round(percentiles[94],1)),0.02,0.15)
    print_subplot(ax,'90th %: ' + str(round(percentiles[89],1)),0.02,0.05)
    print_subplot(ax,'10th %: ' + str(round(percentiles[9],1)),0.5,0.25)
    print_subplot(ax,' 5th %: ' + str(round(percentiles[4],1)),0.5,0.15)
    print_subplot(ax,' 1st %: ' + str(round(percentiles[0],1)),0.5,0.05)

    print_subplot(ax,'Deltas (us)',0.02,0.8)
    print_subplot(ax,'Median: '+str(round(percentiles[49],1)),0.02,0.7)
    print_subplot(ax,'Average: '+str(stats["avg"]),0.02,0.6)
    print_subplot(ax,'Std Dev: '+str(stats["std"]),0.02,0.5)
    print_subplot(ax,'Max: '+str(stats["max"]),0.5,0.6)
    print_subplot(ax,'Min: '+str(stats["min"]),0.5,0.5)

#--------------------------------------------------------------------
# function to add text annotation to subplot
#--------------------------------------------------------------------
def print_subplot(subplot,msg,x,y):
    subplot.annotate(msg,xy=(x,y),xytext=(x,y))

#--------------------------------------------------------------------
#Save png
#--------------------------------------------------------------------
def save_image(filename,fig):
    img_file_name=filename + '.png'

    print 'Saving plot as ' + img_file_name

    default_size=fig.get_size_inches()
    fig.set_size_inches(default_size[0]*2.5,default_size[1]*2.5)
    fig.savefig(img_file_name,dpi=300)

#--------------------------------------------------------------------
#For Chaco text table
#--------------------------------------------------------------------
def build_results_string(label,stats,percentiles):
    return [label,str(stats["min"]),str(stats["avg"]),str(stats["max"]),str(stats["std"]),str(percentiles[0]),str(percentiles[4]),str(percentiles[9]),str(percentiles[89]),str(percentiles[94]),str(percentiles[98])]




