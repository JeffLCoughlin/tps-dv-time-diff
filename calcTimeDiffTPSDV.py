# -*- coding: utf-8 -*-

from subprocess import check_output, CalledProcessError
import numpy as np
import os
import scipy
import math
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys
import matplotlib.colors as colors

reload(sys)
sys.setdefaultencoding('utf8')


def main(argv=None):
    calcTimeDiffTPSDV('OPS-TPS-Time-SES-DV-Period-Epoch.txt','OPS-Time-Diff-TPS-DV.txt')
    # calcTimeDiffTPSDV('test','OPS-Time-Diff-TPS-DV.txt')


def calcTimeDiffTPSDV(filenamein,outfilename):
    """Compute times of transits using for both TPS timestamps and DV linear ephemeris

    Inputs:
    -------------
    filenamein
        The name of the file containing the times of transit, period, and epoch. MUST be sorted by TCE and numerically by TPS transit time

    outfilename
        The name of the output file containing TCEs and their TPS and DV times


    Returns:
    -------------
    None

    Output:
    ----------
    File containing TCEs and their TPS and DV times
    """

    maxt = 2000.0  # Maximum BKJD of the data. Set way in advance just to be safe.

    # Read in the TCE data (tce  ttime  ses  period  epoch)
    data = np.genfromtxt(filenamein, names=True, dtype=None)

    # Open the output file for writing
    outfile = open(outfilename, 'w')

    # Initialize curtce
    curtce = ''

    # Match up TPS and DV transit times
    for dat in data:   # Loop through each TPS transit time
        if(dat['tce'] == curtce):
            t = t - 3*dat['period']  # Go back three epochs just to make sure matching is correct
        else:
            t = dat['epoch']-3*dat['period']  # Start computing the time of transit starting from the given epoch (and a few periods back for good measure)
        curtce = dat['tce']    # Record TCE name
        sw = 0  # Switch value to see if I get any match
        while(t < maxt and sw==0):    # Loop through all possible transit times given the TCE's ephemeris and maximum time of the data set
            if(dat['ttime'] > t-dat['period']/2 and dat['ttime'] < t+dat['period']/2):  # If the TPS transit time is within a half period of the DV transit time
                # Just in case search before and after epoch too
                diffa = np.fabs(t-dat['ttime']-dat['period'])
                diffb = np.fabs(t-dat['ttime'])
                diffc = np.fabs(t-dat['ttime']+dat['period'])
                if(min(diffa,diffb,diffc)==diffa):    # See if one epoch back was best match
                    t = t - dat['period']
                if(min(diffa,diffb,diffc)==diffc):    # See if one epoch forward is best match
                    t = t + dat['period']
                # If diffb (middle epoch) is best match, then no need to do anything
                sw=1  # Record a value was found
                outfile.write("%12s %14.10f %14.10f %14.10f %12.5e\n" % (dat['tce'],dat['ttime'],t,dat['period'],dat['ses']))    # Write the bad TCE name, transit time, and the number 1 to the output file, to be read by robovetter
            t += dat['period']    # Check the TCE's next transit time
        if(sw==0):
            print("No match found for %s at TPS time %15.10f" % (dat['tce'],dat['ttime']))

    # Close the output file
    outfile.close()


# Run main by default
if __name__ == "__main__":
    main()
