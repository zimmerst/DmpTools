#!/bin/env python
'''
Created on Jun 29, 2016

@author: zimmer
'''
from os import listdir
from os.path import join as op_join
from re import findall
from sys import argv

input_folder = argv[1]

for folder in listdir(input_folder):
    release = None
    res = findall("\d+",folder)
    if len(res): release = res[0]
    fullPath = op_join(input_folder, folder)
    bad_files = [f for f in listdir(fullPath) if release not in f]
    if len(bad_files):
        print 'found %i bad files in %s'%(len(bad_files),fullPath)

