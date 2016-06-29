#!/bin/env python
'''
Created on Jun 29, 2016

@author: zimmer
'''
from argparse import ArgumentParser
from os.path import join as op_join
from os.path import dirname
from os import walk

def main(args=None):
    parser = ArgumentParser(usage="Usage: %(prog)s [options]", description="create directories to be created on DPM")
    parser.add_argument("-i","--input",dest="input",type=str,default=".", help="this is the root folder")
    parser.add_argument("-d","--dpmdir",dest="rootdir",type=str,default="/dpm/unige.ch/home/dampe",help="home of dpm")
    parser.add_argument("-x","--xroot",dest="xroot",type=str,default="root://grid05.unige.ch:1094/",help="xrootd server")
    parser.add_argument("--xrootd-only",dest="xrootd_only",action='store_true',default=False, help='if used, show xrootd links instead of DPM')
    opts = parser.parse_args(args)
    print "finding files in %s"%opts.input
    dirs = []
    # walk through folders
    for subdir, dirs, files in walk(opts.input):
        for _file in files:
            out=dirname(op_join(subdir, _file))
            if not out in dirs: dirs.append(out)
    # print output
    for d in dirs: print d



if __name__ == "__main__":
    main()
