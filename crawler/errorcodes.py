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

def identifyEnergyRange(filenamedir):
	'''
	Identifies energy range by looking at the name of the file (not at the event header)
	
	String manipulations are evil
	'''
	
	filename = os.path.basename(filenamedir)
	
	start = filename.find('_')+1
	mid = filename.find('V_')+1
	emin_str = filename[start:mid]
	
	secondhalf = filename[mid+1:]
	end_2 = secondhalf.find('V')+1
	emax_str = secondhalf[0:end_2]
	
	if "MeV" in emin_str: e_min = int(emin_str.split('M')[0]) * 1.
	elif "GeV" in emin_str: e_min = int(emin_str.split('G')[0]) * 1e+3
	elif "TeV" in emin_str: e_min = int(emin_str.split('T')[0]) * 1e+6
	else: raise Exception("Energy min - not recognised. "+emin_str)
	
	if "MeV" in emax_str: e_max = int(emax_str.split('M')[0]) * 1.
	elif "GeV" in emax_str: e_max = int(emax_str.split('G')[0]) * 1e+3
	elif "TeV" in emax_str: e_max = int(emax_str.split('T')[0]) * 1e+6
	else: raise Exception("Energy max - not recognised. "+emax_str)
	
	return e_min, e_max


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
				
				if iteration['emin'] > 1e+6: key1 = str(iteration['emin']/1e+6)+'TeV'
				elif iteration['emin'] > 1e+3: key1 = str(iteration['emin']/1e+3)+'GeV'
				else: key1 = str(iteration['emin'])+'MeV'
				
				if iteration['emax'] > 1e+6: key2 = str(iteration['emax']/1e+6)+'TeV'
				elif iteration['emax'] > 1e+3: key2 = str(iteration['emax']/1e+3)+'GeV'
				else: key2 = str(iteration['emax'])+'MeV'
				
				key = key1 + '_' + key2
				try: 
					dicEnergy[key].append(iteration['lfn'])
				except KeyError:
					dicEnergy[key] = [iteration['lfn']]
					
		for key in dicEnergy.keys():
			outstring = dirname + '/energies/' + key + '.txt'
			
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

