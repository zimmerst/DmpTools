'''

Merger v0.2.0

How to run:
> python merger.py files.txt reductionfactor
        files.txt is an ASCII list of files
        reductionfactor is a number, how many files you want to merge into a single one (if 100, then one new file corresponds to 100 old)

Terminal output:
    A lot of output caused by the DmpSoftware. At the end, the run time is written to terminal

Files output:
    Creates two directories:
        ./merger_out/*dataset*/  contains the output root files, using the 5-digits convention we discussed.
        ./merger_data/*dataset*/  contains:
                                        - notmerged.txt : a text file containing the list of files that have not been merged (end of chunk). Empty if everything has been merged.
                                        - merged.yaml :  a dictionary which maps new files to old files
                                        - fmerged.txt : list of files that got merged

Other features:
    The script checks for existence of output files, and does not run on files that already exist. So it can resume where it stopped
	Checks the input files to look for bad PDG ID. Can be disabled to gain computation time
	Can be called with a custom file number index

'''


from ROOT import gSystem
from glob import glob
from sys import argv
gSystem.Load("libDmpEvent.so")
from ROOT import DmpChain, TChain, TFile, DmpRunSimuHeader, DmpEvtSimuPrimaries
from os import mkdir
from os.path import isdir, basename, isfile
from time import time, strftime, gmtime
import cPickle as pickle 
from yaml import dump as ydump
from tqdm import tqdm
from copy import deepcopy


class Merger(object):
	'''
	Merger class
	
	Initialise with the list of files to be merged, and the reduction factor (i.e. how many files to merge into a single one)
	'''
	
	def __init__(self, textfile, reductionfactor, progress=True, checkPart=True, rld=True, i=0):
		
		self.t0 = time()
		self.progress = progress
		self.debug = debug 
		
		self.checkPart = checkPart
		self.rld = rld
		
		self.index = i
		
		self.mergedfiles = []
		self.notmerged = []
		self.rf = int(reductionfactor)
		self.tomerge = [f.replace("\n","") for f in open(textfile,'r').readlines()]
		self.basefiles = deepcopy(self.tomerge)
		self.nroffiles = len(self.basefiles)
		self.nrofsteps = self.nroffiles / self.rf
		
		self.equivalence = {}
		self.badPDGId = []
		
		temp_str = basename(self.tomerge[0])
		temp_int = temp_str.find('.')				
		self.subdir = '/' + temp_str[0:temp_int]
		self.configfile = 'merger_data' + self.subdir + '/self.pick'
		del temp_str, temp_int
		for x in ['merger_out','merger_data']:			# merger_out contains output, merger_data contains self data
			if not isdir(x):
				mkdir(x)
			if not isdir(x + self.subdir):
				mkdir(x + self.subdir)
		
		if isfile(self.configfile):
			self.load()
				
	def getRunTime(self):
		return (time() - self.t0)
	def getMerged(self):
		return self.mergedfiles
	def getToMerge(self):
		return self.notmerged
		
	def testPdgId(self, fname):
		'''
		test if the particle ID is good. Adapted from Stephan's work on the crawler
		'''
		bn = basename(fname).split(".")[0].split("-")[0]
		if (not bn.startswith("all")) or (("bkg" or "background" or "back") in bn.lower()):
			return True
		else:
			try:
				tree = mcprimaries = None
				tree = TChain("CollectionTree")
				tree.Add(fname)
				tree.SetBranchStatus("DmpEvtSimuPrimaries",1)
				branch = tree.GetBranch("DmpEvtSimuPrimaries")
				mcprimaries = DmpEvtSimuPrimaries()
				tree.SetBranchAddress("DmpEvtSimuPrimaries", mcprimaries)
				branch.GetEntry(0)
				tree.GetEntry(0)
				entry = tree.GetEntry(0)
				pdg_id = int(mcprimaries.pvpart_pdg)
				if pdg_id > 10000:
					pdg_id = int(pdg_id/10000.) - 100000
				pdgs = dict(Proton=2212, Electron=11, Muon=13, Gamma=22,He = 2, Li = 3, Be = 4, B = 5, C = 6, N = 7, O = 8)
				particle = bn.replace("all","")
				if "flat" in particle:
					particle = bn.replace("flat","")
				assert particle in pdgs.keys(), "particle type not supported"
				if pdgs[particle] != pdg_id:
					msg = "wrong PDG ID! particle_found={part_found} ({PID}); particle_expected={part_exp} ({particle})".format(part_exp=int(pdgs[particle]),
																										  part_found=int(pdg_id),particle=particle,
																										  PID=dict(zip(pdgs.values(),pdgs.keys()))[pdg_id])
					raise ValueError(msg)
			except Exception as err:
				del tree, mcprimaries
				#~ raise Exception(err.message)
				return False

			return True
		
	def save(self):
		'''
		Saves current status on disk to be able to run it later
		'''
		with open(self.configfile,'w') as f:
			pickle.dump( self  , f)
		
	def unpickle(fname):
		with open(fname,'r') as f:
			return pickle.load(fname)
		
	def write(self):
		'''
		Write metadata once run is over
		'''
		self.yamlfile = 'merger_data' + self.subdir + '/merged.yaml'
		with open(self.yamlfile,'w') as f:
			ydump( self.equivalence , f)
		self.notmergedfile = 'merger_data' + self.subdir + '/notmerged.txt'
		with open(self.notmergedfile,'w') as g:
			for item in self.notmerged:
				g.write(item + '\n')
		self.mergedlist = 'merger_data' + self.subdir + '/mfiles.txt'
		with open(self.mergedlist,'w') as h:
			for item in self.mergedfiles:
				h.write(item + '\n')
		
	def run(self):
		'''
		Splits filelist into chunks and run merge() on each chunk. Calls save() at each iteration
		and write() at the end
		'''

		loop = xrange(self.nrofsteps)
		if self.progress: loop = tqdm(loop)
		for i in loop:
			
			if len(self.tomerge) < self.rf:
				break
			
			self.chunk = []
			for k in xrange(self.rf):
				self.chunk.append( self.tomerge.pop(0) )
			
			while True:
				try:
					self.merge( self.chunk , self.index )
					self.index = self.index + 1
					break
				except ReferenceError:				# File cannot be accessed over Xrootd because reasons. Raises a ReferenceError due to null-pointer
					pass							# Since error is temporary, we ignore it.
				except:
					raise
					
			self.mergedfiles = self.mergedfiles + self.chunk
			self.save()
		
		self.notmerged = deepcopy(self.tomerge)		# Files left over.
		
		self.write()
		
	def merge(self,filelist, i):
		'''
		Takes a python list "filelist" as argument, merges all the root files from that list
		into an output root file, whose name is decided by "i"
		'''
		# String manipulation to build output name
		outfile = 'merger_out' + self.subdir + '/'
		if 'reco' in filelist[0]:
			temp_int = basename(filelist[0]).find('.reco') - 6
			temp_index = "%05d" % (i,)
			outfile = outfile + basename(filelist[0])[0:temp_int] + temp_index + '.reco.root'
			del temp_int, temp_index
		elif 'mc' in filelist[0]:
			temp_int = basename(filelist[0]).find('.mc') - 6
			temp_index = "%05d" % (i,)
			outfile = outfile + basename(filelist[0])[0:temp_int] + temp_index + '.mc.root'
			del temp_int, temp_index
		else:
			raise Exception("Could not identify file type. Looking for '.reco.root' or '.mc.root'")
		
		if isfile(outfile): 
			return
		
		# Open files, build TChain
		dmpch = DmpChain("CollectionTree")
		metachain = TChain("RunMetadataTree")
		for f in filelist:
			if self.checkPart:
				if not self.testPdgId(f):
					self.badPDGId.append(f)
					continue
			dmpch.Add(f)
		metachain.Add(filelist[0])
		
		# Get Metadata values from "old" files
		nrofevents = 0
		for f in filelist:
			fo = TFile.Open(f)
			rmt = fo.Get("RunMetadataTree")
			simuheader = DmpRunSimuHeader()
			rmt.SetBranchAddress("DmpRunSimuHeader",simuheader)
			rmt.GetEntry(0)
			nrofevents += simuheader.GetEventNumber()
			fo.Close()
			
		fob = TFile.Open(filelist[0])
		rmt = fob.Get("RunMetadataTree")
		simuheader = DmpRunSimuHeader()
		rmt.SetBranchAddress("DmpRunSimuHeader",simuheader)
		rmt.GetEntry(0)
		runNumber = simuheader.GetRunNumber()
		spectrumType = simuheader.GetSpectrumType()
		sourceType = simuheader.GetSourceType()
		vertexRadius = simuheader.GetVertexRadius()
		sourceGen = simuheader.GetSourceGen()
		maxEne = simuheader.GetMaxEne()
		minEne = simuheader.GetMinEne()
		version = simuheader.GetVersion()
		fluxFile = simuheader.GetFluxFile()
		orbitFile = simuheader.GetOrbitFile()
		prescale = simuheader.GetPrescale()
		startMJD = simuheader.GetMJDstart()
		stopMJD = simuheader.GetMJDstop()
		seed = simuheader.GetSeed()
		fob.Close()
		
		# Write new file
		tf = TFile(outfile,"RECREATE")
		ot = dmpch.CloneTree(-1,"fast")
		om = metachain.CloneTree(0)
		simhdr = DmpRunSimuHeader()
		om.SetBranchAddress("DmpRunSimuHeader",simhdr)
		for i in xrange(metachain.GetEntries()):
			metachain.GetEntry(i)
			simhdr.SetEventNumber(nrofevents)
			simhdr.SetRunNumber(runNumber)
			simhdr.SetSpectrumType(spectrumType)
			simhdr.SetSourceType(sourceType)
			simhdr.SetVertexRadius(vertexRadius)
			simhdr.SetSourceGen(sourceGen)
			simhdr.SetMaxEne(maxEne)
			simhdr.SetMinEne(minEne)
			simhdr.SetVersion(version)
			simhdr.SetFluxFile(fluxFile)
			simhdr.SetOrbitFile(orbitFile)
			simhdr.SetPrescale(prescale)
			simhdr.SetMJDstart(startMJD)
			simhdr.SetMJDstop(stopMJD)
			simhdr.SetSeed(seed)
			om.Fill()
		tf.Write()
		tf.Close()
		
		self.equivalence[basename(outfile)] = filelist
		
		for x in [dmpch,metachain,nrofevents,runNumber,spectrumType,sourceType,vertexRadius,sourceGen,maxEne,minEne,version,fluxFile,orbitFile,prescale,startMJD,stopMJD,seed,simuheader,rmt,simhdr,outfile]:
			try:
				del x
			except:
				continue
		

if __name__ == '__main__' :
	
	with open(sys.argv[1],'r') as g:
		for line in g:
			configfile = line.replace('\n','')
			break
	configfile = basename(configfile)
	temp_int = configfile.find('.')				
	subdir = '/' + configfile[0:temp_int]
	configfile = 'merger_data' + subdir + '/self.pick'
	
	if isfile(configfile):
		a = Merger.unpickle(configfile)
		a.run()
	else:
		a = Merger(argv[1],argv[2])
		a.run()
	
	print 'Run time: ', str(strftime('%H:%M:%S', gmtime( a.getRunTime() )))
