'''

extractGoodFiles

Given the output of the crawler, extracts good files and writes a new json file to a given directory

usage: 
	> python extractGoodFiles.py /path/to/json/ /output/path

'''

from __future__ import absolute_import, print_function

import json
import os
import sys
from glob import glob
from shutil import copy

from errorcodes import json_load_byteified


def run(infile,outdir):
	
	goodFiles = []
	
	with open(infile,'r') as f:	
		diclist = json_load_byteified(f)
		
	for x in diclist:
		if x['good']:
			goodFiles.append(x)
			
	if outdir[-1] != '/' : outfile = outdir+'/'+os.path.basename(infile)
	else: outfile = outdir+os.path.basename(infile)
	
	if os.path.isfile(outfile):
		raise IOError("Cannot write "+outfile+". File exists!")
	
	with open(outfile,'w') as f:
		json.dump(goodFiles,f)



if __name__ == '__main__':
	
	run(sys.argv[1],sys.argv[2])
