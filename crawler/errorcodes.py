'''

To run after the crawler. Either 
	> python errorcodes.py listofjsonfiles.txt
	or
	> python errorcodes.py file.json

Script will browse the json file(s) and make filelists based on error code. Also includes good files.
Output under  ./outputs/*dataset*/

If multiple energy ranges found, additional output under   ./outputs/*dataset*/energies/

Error codes:
0 : No error, file is good
1001 : Missing branches
1002 : House-Keeping tree is missing in flight data
1003 : Bad particle
1004 : Zero events - file is readable
2000 : Cannot access file / cannot read file
1005 : Events outside of energy range
3000 : C++ internal error

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
	
	
	# Identify energy range:
	if "10TeV_100TeV" in diclist[0]['lfn']:
		energyMin = 1e+7
	elif "10GeV_100GeV" in diclist[0]['lfn']:
		energyMin = 1e+4
	elif "100GeV_10TeV" in diclist[0]['lfn']:
		energyMin = 1e+5
	elif "1GeV_100GeV" in diclist[0]['lfn']:
		energyMin = 1e+3
	else:
		raise Exception("Energy range not recognised")
	
	
	fichiers = {'0':[],'1001':[],'1002':[],'1003':[],'1004':[],'2000':[],'1005':[],'3000':[]}
	tailles = []
	for i in range(8):
		tailles.append([])
	emins = []
	emaxs = []
	
	for iteration in diclist:
		
		# List error codes
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
			
		# Check for energy range
		if iteration['error_code'] == 0:
			emins.append(iteration['emin'])
			emaxs.append(iteration['emax'])
			
	if len(set(emins)) > 1 or len(set(emaxs)) > 1:		# Multiple energy ranges found
		print "Energies found, lower bound: ", list(set(emins))
		print "Energies found, upper bound: ", list(set(emaxs))
		print "Found multiple energy ranges! File: ", filename.replace('.json','')
		badEnergies = True
	elif energyMin not in emins: 		# Wrong energy range
		badEnergies = True
		print "Found bad energy range! File: ", filename.replace('.json','')
	else:
		badEnergies = False
	
	# Write results		
	if boolwrite:
		for blarg in fichiers.keys():
			
			if not os.path.isdir('outputs'):
				os.mkdir('outputs')
			
			dirname = './outputs/' + os.path.splitext(os.path.basename(filename))[0]
			if not os.path.isdir(dirname):
				os.mkdir(dirname)
			outstring = dirname + '/error' + blarg + '.txt'
				
			with open(outstring,'w') as thefile:
				for item in fichiers[blarg]:
					thefile.write("%s\n" % item)
		if badEnergies:
			if not os.path.isdir(dirname+'/energies'): os.mkdir(dirname+'/energies')
			
			dicEnergy = {}
			for x in list(set(emaxs)):
				dicEnergy[str(x)] = []
			for iteration in diclist:
				if iteration['error_code'] == 0:
					dicEnergy[str(iteration['emax'])].append(iteration['lfn'])
			
			for key in dicEnergy.keys():
				if float(key) == 1e+5: erange='10GeV_100GeV.txt'
				elif float(key) == 1e+7: erange='100GeV_10TeV.txt'
				elif float(key) == 1e+8: erange='10TeV_100TeV.txt'
				else: raise Exception("Energy range not recognised!")
				outstring = dirname + '/energies/' + erange
				
				with open(outstring,'w') as thefile:
					for item in dicEnergy[key]:
						thefile.write("%s\n" % item)
				
	return fichiers, tailles
	

if __name__ == '__main__':
	
	if ".json" in sys.argv[1]:		# Only one json file provided
		filecount, filesize = _ana(sys.argv[1],boolwrite=True)
		
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
