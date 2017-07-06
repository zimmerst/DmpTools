'''

To run after the crawler. Either 
	> python errorcodes.py listofjsonfiles.txt
	or
	> python errorcodes.py file.json

Script will browse the json file(s) and make filelists based on error code. Also includes good files.
Output under  ./outputs/*dataset*/

Secondary output:  file.good.json
	List of dictionaries containing only good files

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
	'''
	Crawler output is unicode. Change to UTF-8 for better handling
	'''
	return _byteify(
		json.load(file_handle, object_hook=_byteify),
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

def identifyEnergyRange(filename):
	'''
	Identifies energy range by looking at the name of the file (not at the event header)
	'''
	if "10TeV_100TeV" in filename:
		energyMin = 1e+7
		energyMax = 1e+8
	elif "10GeV_100GeV" in filename:
		energyMin = 1e+4
		energyMax = 1e+5
	elif "100GeV_10TeV" in filename:
		energyMin = 1e+5
		energyMax = 1e+7
	elif "1GeV_100GeV" in filename:
		energyMin = 1e+3
		energyMax = 1e+5
	else:
		raise Exception("Energy range not recognised")
	return energyMin, energyMax


def ana(filename):
	if '.json' not in filename:
		raise IOError('Not a .json file')
	
	with open(filename,'r') as f:	
		diclist = json_load_byteified(f)
	
	eMin,eMax = identifyEnergyRange(diclist[0]['lfn'])
	emins = []
	emaxs = []
	
	# Explicitly have one list per possible error code - at the end I want empty files for error codes that did not appear (instead of having no file at all)
	fichiers = {'0':[],'1001':[],'1002':[],'1003':[],'1004':[],'2000':[],'1005':[],'3000':[]}
	
	goodDicList = [] 		# Build a new json file with only good files

	for iteration in diclist:
		fichiers[str(iteration['error_code'])].append(iteration['lfn'])
		if iteration['error_code'] == 0:
			emins.append(iteration['emin'])
			emaxs.append(iteration['emax'])
			goodDicList.append(iteration)
			
	with open(filename.replace('.json','.good.json'),'w') as f:
		json.dump(goodDicList,f)
			
	if len(set(emins)) > 1 or len(set(emaxs)) > 1:		# Multiple energy ranges found
		print "Found multiple energy ranges! File: ", filename.replace('.json','')
		badEnergies = True
	elif eMin not in emins or eMax not in emaxs: 		# Wrong energy range
		badEnergies = True
		print "Found bad energy range! File: ", filename.replace('.json','')
	else:
		badEnergies = False
	
	# Write results	
	dirname = './ana/' + os.path.splitext(os.path.basename(filename))[0]
	for d in ['ana',dirname]:
		if not os.path.isdir(d): os.mkdir(d)
		
	for k in fichiers.keys():
		outstring = dirname + '/error' + k + '.txt'
		with open(outstring,'w') as thefile:
			for item in fichiers[k]:
				thefile.write("%s\n" % item)
	if badEnergies:
		if not os.path.isdir(dirname+'/energies'): os.mkdir(dirname+'/energies')
		
		dicEnergy = {}
		for x in list(set(emins)):
			dicEnergy[str(x)] = []
		for iteration in diclist:
			if iteration['error_code'] == 0:
				dicEnergy[str(iteration['emin'])].append(iteration['lfn'])
		
		for key in dicEnergy.keys():
			if float(key) == 1e+4: erange='10GeV_100GeV.txt'
			elif float(key) == 1e+5: erange='100GeV_10TeV.txt'
			elif float(key) == 1e+7: erange='10TeV_100TeV.txt'
			elif float(key) == 1e+3: erange='1GeV_100GeV.txt'
			else: raise Exception("Energy range not recognised!")
			outstring = dirname + '/energies/' + erange
			
			with open(outstring,'w') as thefile:
				for item in dicEnergy[key]:
					thefile.write("%s\n" % item)
	
	
	

if __name__ == '__main__':
	
	if ".json" in sys.argv[1]:		# Only one json file provided
		ana(sys.argv[1])
	else:							# ASCII list of json files provided
		inputlist = []
		with open(sys.argv[1],'r') as f:
			for lines in f:
				inputlist.append(lines.replace('\n',''))		
		for fichier in inputlist:
			ana(fichier)

