#Create emission files from csv

import shutil
import pandas as pd
from netCDF4 import Dataset
import os
import numpy as np
import sys
from PseudoNetCDF.sci_var import getvarpnc, slice_dim
from PseudoNetCDF.pncgen import pncgen
from PseudoNetCDF.conventions.ioapi import add_ioapi_from_ioapi
import argparse
from warnings import warn
parser = argparse.ArgumentParser(description = 'Make CSV files into netcdf')
parser.add_argument('-v', '--verbose', action = 'count', default = 0, help = 'Add more -v for more verbosity')
parser.add_argument('-t', '--template', default = '../data/in/emisd04_26', help = 'File to use as a template')
parser.add_argument('-O', '--clobber', default = False, action = 'store_true', help = 'If clobber, existing files will be overwritten.')
parser.add_argument('csvpath', nargs = '+', help = 'one or more csv files')
args = parser.parse_args()
templatepath = args.template #'template.nc'

csvpaths = args.csvpath

for path in csvpaths:
    outpaths = ['../data/out/' + os.path.basename(path.replace('.csv', '.nc'))] #for path in csvpaths]

hours=['E00h','E01h','E02h','E03h','E04h','E05h','E06h','E07h','E08h','E09h','E10h','E11h','E12h','E13h','E14h','E15h','E16h','E17h','E18h','E19h','E20h','E21h','E22h','E23h','E24h'][:-1]

# Adjust emission to UTC (BOG = UTC-5)
hours = np.roll(np.array(hours), 5).tolist()
# adding 0 UTC as the last hour
hours += [hours[0]]
hours = [hours[0]]+hours
for csvpath, outpath in zip(csvpaths, outpaths):
    if not args.clobber and os.path.exists(outpath):
        if os.path.getmtime(csvpath) > os.path.getmtime(outpath):
            print('WARNING: %s is newer than %s; not updating. Use -O to overwrite' % (csvpath, outpath))
        if os.path.getmtime(__file__) > os.path.getmtime(outpath):
            print('WARNING: script is newer than %s; not updating. Use -O to overwrite' % (outpath,))
        continue
    csvfile = pd.read_csv(csvpath)
    unique_vars = np.unique(np.char.replace([v for v in csvfile['POLNAME'].values], 'BEN', 'BENZENE')).tolist()
    aggdata = csvfile.pivot_table(index = ('POLNAME', 'ROW', 'COL'), aggfunc = np.sum)
    oldpolname = None
    outfile = getvarpnc(Dataset(templatepath, 'r+'), ['TFLAG'] + unique_vars)
    add_ioapi_from_ioapi(outfile)
#    outfile.variables['TFLAG'][:, :, 0] = np.arange(0, 25)[:, None]
#    outfile.variables['TFLAG'][:, :, 0] = 2014001
    print('Working on: ' + csvpath)
    for (polname, rowi, coli), groupdata in aggdata.iterrows():
        if args.verbose > 2: print(polname)
        if polname != oldpolname:
            if not oldpolname is None:
                if args.verbose > 0: print('Writing out ' + polname + ' to ' + var.long_name)
                var[0:26, 0, :, :] = temp[0:26, 0, :, :]
            if args.verbose > 0: print('Starting ' + polname)
            if polname=='BEN':
                var = outfile.variables['BENZENE']
            elif polname!='CO2':
                var = outfile.variables[polname]
            else:
                warn('WARNING: skipping %s in %s' % (polname, csvpath))
                oldpolname = None
                continue
            temp = np.zeros_like(var[:])
            oldpolname = polname
        temp[0:26, 0, rowi, coli] += np.array([groupdata[hours[k]].sum() for k in range(0, 26)])
    # catch the last pollutant
    var[0:26, 0, :, :] = temp[0:26, 0, :, :]
    pncgen(outfile, outpath, verbose = args.verbose)
