import os,sys
from math import *

inputdir = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKPlotsForPaper/NominalFit/'

dspi_data_fit_prefix = 'DsPiTimeFit_'
dspi_mc_fit_prefix   = 'SplineLog_DsPiMC_'
dsk_mc_fit_prefix    = 'SplineLog_DsKMC_'

suffix = '.out'

# first dir entry is data fit suffix, second is MC suffix
BDTG_BINS            = { "BDTGA"    : '03_10_04_15',
                         "BDTG1"    : '03_09_04_15',
                         "BDTG3"    : '09_10_075_15',
                         "BDTG06"   : '06_10_04_15' }

for bin in BDTG_BINS :
    datafile = open(inputdir+dspi_data_fit_prefix+bin+suffix)
    dspimcfile = open(inputdir+dspi_mc_fit_prefix+BDTG_BINS[bin]+suffix)
    dskmcfile = open(inputdir+dsk_mc_fit_prefix+BDTG_BINS[bin]+suffix)

    print 72*'#'
    print 72*'#'
    print 'Creating DsK acceptance for BDTG bin',bin
    print 72*'-'
    print 'Obtain the DsPi data acceptance first\n'
    # First get the data result in this bin
    for line in datafile :
        if line.find('tacc_knots') > -1:
            print 'Knots are at',line.split('=')[1]
        if line.find('FinalValue') > -1:
            break
    skip = 2
    splineterms_dspi_data = []
    for line in datafile :
        if skip > 0 :
            skip -= 1
            continue
        if line.find('var')==-1 :
            break
        else :
            splineterms_dspi_data.append(float(line.split()[2]))
    datafile.close()
    print 'Spline terms for data DsPi fit are',splineterms_dspi_data
    print 72*'-'
    print 'Obtain the DsPi MC acceptance next\n'
    for line in dspimcfile :
        if line.find('Calculating sum-of-weights-squared') > -1 :
            break
    for line in dspimcfile :
        if line.find('NO.   NAME') > -1 :
            break
    splineterms_dspi_mc = []
    for line in dspimcfile :
        if line.find('var')== -1 :
            break
        else :
            splineterms_dspi_mc.append(float(line.split()[2]))
    dspimcfile.close()
    print 'Spline terms for MC DsPi fit are',splineterms_dspi_mc
    print 72*'-'
    print 'Obtain the DsK MC acceptance next\n'
    for line in dskmcfile :
        if line.find('Calculating sum-of-weights-squared') > -1 :
            break
    for line in dskmcfile :
        if line.find('NO.   NAME') > -1 :
            break
    splineterms_dsk_mc = []
    for line in dskmcfile :
        if line.find('var')== -1 :
            break
        else :
            splineterms_dsk_mc.append(float(line.split()[2]))
    dskmcfile.close()
    print 'Spline terms for MC DsK fit are',splineterms_dsk_mc
    # Now compute the DsK data acceptance
    splineterms_dsk_data = []
    for i in range(0,len(splineterms_dspi_data)) :
        splineterms_dsk_data.append(float(splineterms_dspi_data[i]*splineterms_dsk_mc[i]/splineterms_dspi_mc[i]))
    print 'Spline terms for data DsK fit are',splineterms_dsk_data
