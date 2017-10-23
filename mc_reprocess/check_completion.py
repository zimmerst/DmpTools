'''

Check completion: prints to std:out the number of files to be processed, and the number of files already processed

Usage:
	> python check_completion.py /path/to/task /path/to/output release_tag
	
Example:
	Running:
		> python check_completion.py /dampe/data3/users/public/crawler/txt/v6/allProton-v5r4p2_1GeV_15GeV.txt /dampe/data3/XROOTD_DIR/MC/reco/v6r0p0/ v6r0p0
	Output:
		allProton-v5r4p2_1GeV_15GeV : 325/1485

'''

from __future__ import print_function, absolute_import

import os
import sys
from submit import mc2reco

if __name__ == '__main__':
	
	n_done = 0
	
	files = []
	
	with open(sys.argv[1],'r') as f:
		for line in f:
			files.append(line.replace('\n',''))
	outputDir = sys.argv[2]
	tag = sys.argv[3]
	
	n_total = len(files)
	
	for f in files:
		if os.path.isfile(mc2reco(f,version=tag,newpath=outputDir)):
			n_done += 1
			
	taskName = os.path.basename(sys.argv[1]).replace('.txt','')
	
	print(taskName,' : ',n_done,'/',n_total)
	
	
