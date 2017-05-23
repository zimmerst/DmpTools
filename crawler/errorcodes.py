'''

To run after the crawler. Either 
	> python errorcodes.py listofjsonfiles.txt
	or
	> python errorcodes.py file.json

Script will browse the json file(s) and make filelists based on error code. Also includes good files.
Output under  ./outputs/*dataset*/

Error codes:
0 : No error, file is good
1001 : Missing branches
1002 : House-Keeping tree is missing in flight data
1003 : Bad particle
1004 : Zero events - file is readable
2000 : Cannot access file / cannot read file

'''


import json
import os
import sys

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )
def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )
def _byteify(data, ignore_dicts = False):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    return data


def _ana(filename,boolwrite=False):
	if not '.json' in filename:
		raise IOError('Not a .json file')
	
	with open(filename,'r') as f:	
		diclist = json_load_byteified(f)
	
	
	fichiers = {'0':[],'1001':[],'1002':[],'1003':[],'1004':[],'2000':[],'1005':[],'3000':[]}
	tailles = []
	for i in range(8):
		tailles.append([])
	
	for iteration in diclist:
		
		if iteration['error_code'] == 0:
			fichiers['0'].append(iteration['lfn'])
			tailles[0].append(iteration['nevts'])
		elif iteration['error_code'] == 1001:
			fichiers['1001'].append(iteration['lfn'])
			tailles[1].append(iteration['nevts'])
		elif iteration['error_code'] == 1002:
			fichiers['1002'].append(iteration['lfn'])
			tailles[2].append(iteration['nevts'])
		elif iteration['error_code'] == 1003:
			fichiers['1003'].append(iteration['lfn'])
			tailles[3].append(iteration['nevts'])
		elif iteration['error_code'] == 1004:
			fichiers['1004'].append(iteration['lfn'])
			tailles[4].append(iteration['nevts'])
		elif iteration['error_code'] == 2000:
			fichiers['2000'].append(iteration['lfn'])
			tailles[5].append(iteration['nevts'])
		elif iteration['error_code'] == 1005:
			fichiers['1005'].append(iteration['lfn'])
			tailles[6].append(iteration['nevts'])
		elif iteration['error_code'] == 3000:
			fichiers['3000'].append(iteration['lfn'])
			tailles[7].append(iteration['nevts'])
		else:
			raise Exception('Unmanaged error code:' + str(iteration['error_code']))
			
	if boolwrite:
		for blarg in fichiers.keys():
			
			if not os.path.isdir('outputs'):
				os.mkdir('outputs')
			
			dirname = './outputs/' + os.path.splitext(os.path.basename(filename))[0]
			if not os.path.isdir(dirname):
				os.mkdir(dirname)
			outstring = dirname + '/' + 'error' + blarg + '.txt'
				
			with open(outstring,'w') as thefile:
				for item in fichiers[blarg]:
					thefile.write("%s\n" % item)
				
	return fichiers, tailles
	

if __name__ == '__main__':
	
	if ".json" in sys.argv[1]:		# Only one json file provided
		filecount, filesize = _ana(sys.argv[1],boolwrite=False)
		
	else:							# ASCII list of json files provided
		inputlist = []
		with open(sys.argv[1],'r') as f:
			for lines in f:
				inputlist.append(lines.replace('\n',''))
		
			filecounts = []
			filesizes = []
			totals = {'0':[],'1001':[],'1002':[],'1003':[],'1004':[],'2000':[],'1005':[],'3000':[]}
		
		# Loop on .json files	
		for fichier in inputlist:
			
			cnt, sze = _ana(fichier)
			filecounts.append(cnt)
			filesizes.append(sze)
			
			for k in totals.keys() :
				totals[k] = totals[k] + cnt[k]
		
		# Loop over, writing to file		
		for k in totals.keys() :
			outname = './out_ana/out_err' + k + '_' + sys.argv[1]
			with open(outname,'w') as f:
				for item in totals[k]:
					f.write("%s\n" % item)
		print '----------------------------------------------'
		print ' --- TOTAL --- '
		a = 0
		for k in totals.keys():
			a = a + len(totals[k])
			print k, " : ", len(totals[k])
		print "Total : ", a
