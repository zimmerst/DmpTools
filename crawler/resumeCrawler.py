'''

resumeCrawler

Use this when an instance of crawl_filelist.sh is killed before it finishes.
Script sets up a new working dir in ./p2/ with the remaining part to be crawled

Dirty workaround to allow the crawler to skip files that were already crawled 

Usage:
	> python resumeCrawler.py listOfFiles.txt crawlerOutput.json
	

'''

from __future__ import absolute_import, print_function

import json
import os
import sys
from glob import glob
from shutil import copy

from errorcodes import json_load_byteified


def run(task,crawled):
	
	if os.path.isdir('p2'):
		print("Detected a task for crawler part2")
		return
	
	files = []
	with open(task,'r') as f:
		for lines in f:
			files.append(lines.replace('\n',''))
			
	with open(crawled,'r') as f:	
		diclist = json_load_byteified(f)
		
	if len(files) == len(diclist):
		print("Crawler done, nothing to resume")
		return
	
	filesCrawled = []
	filesToCrawl = []
	
	for iteration in diclist:
		filesCrawled.append(iteration['lfn'])
	for f in files:
		if f not in filesCrawled:
			filesToCrawl.append(f)
	
	print("Found ", len(filesToCrawl), " files to be crawled")
			
	os.mkdir('p2')
	newName = task.replace('.txt','.part2.txt')
	with open('p2/'+newName,'w') as f:
		for item in filesToCrawl:
			f.write(item+'\n')
	
	bashScripts = glob('*.sh')
	for x in bashScripts: copy(x,'./p2/')
	
	with open('p2/badFiles.bad','w') as f:
		os.utime('p2/badFiles.bad',None)
	
	
if __name__ == '__main__':
	
	task = sys.argv[1]
	crawled = sys.argv[2]
	
	run(task,crawled)
