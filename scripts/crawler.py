"""

@author: zimmer
@date: 2017-01-19
@comment: a first implementation of a crawler of DAMPE data, depending on DAMPE framework.
@todo: implement livetime calculation.

"""
from sys import argv
from ROOT import gSystem, gROOT
from os.path import getsize
#from tqdm import tqdm
gROOT.SetBatch(True)
gROOT.ProcessLine("gErrorIgnoreLevel = 3002;")
from XRootD import client

infile = argv[1]

res = gSystem.Load("libDmpEvent")
if res != 0:
    raise ImportError("could not import libDmpEvent, mission failed.")
from ROOT import TChain, DmpChain
DmpChain.SetVerbose(0)

types = ("mc:simu","mc:reco","2A")

branches = {
    "mc:simu":['EventHeader', 'DmpSimuStkHitsCollection', 'DmpSimuPsdHits', 'DmpSimuNudHits0Collection',
               'DmpSimuNudHits1Collection', 'DmpSimuNudHits2Collection', 'DmpSimuNudHits3Collection',
               'DmpBgoSptStruct', 'DmpSimuBgoHits', 'DmpEvtSimuHeader', 'DmpEvtSimuPrimaries',
               'DmpTruthTrajectoriesCollection', 'DmpSimuSeondaryVtxCollection', 'DmpEvtOrbit'],
    "mc:reco":['StkKalmanTracks', 'DmpEvtBgoHits', 'DmpSimuBgoHits', 'DmpEvtBgoRec', 'EventHeader',
               'DmpEvtNudRaw', 'DmpEvtSimuPrimaries', 'StkClusterCollection', 'DmpStkLadderAdcCollection',
               'DmpStkEventMetadata', 'DmpPsdHits', 'DmpSimuPsdHits', 'DmpEvtPsdRec', 'DmpGlobTracks',
               'DmpEvtOrbit', 'DmpEvtSimuHeader', 'DmpTruthTrajectoriesCollection'],
    "2A":['EventHeader', 'DmpEvtPsdRaw', 'DmpPsdHits', 'DmpEvtBgoRaw', 'DmpEvtBgoHits', 'StkClusterCollection',
          'DmpStkLadderAdcCollection', 'DmpStkEventMetadata', 'StkKalmanTracks', 'DmpEvtNudRaw', 'EvtAttitudeContainer',
          'DmpEvtBgoRec', 'DmpEvtPsdRec', 'DmpGlobTracks']
}

# fixme: this wraps the null pointer testing.

#def md5sum(fname):
#    from subprocess import Popen, PIPE
#    cmd = "md5sum {fname}".

def checkBranches(tree, branches):
    for b in branches:
        res = tree.FindBranch(b)
        if res is None:
            raise Exception("missing branch %s",b)
    return True

def testPdgId(fname):
    from os.path import basename
    bn = basename(fname).split(".")[0].split("-")[0]
    if not bn.startswith("all"):
        print 'non-standard sample, skip'
        return True
    elif ("bkg" or "background" or "back") in bn.lower():
        print 'background sample, skip'
        return True
    else:
        from ROOT import DmpEvtSimuPrimaries
        tree = mcprimaries = None
        try:
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
            #print particle
            assert particle in pdgs.keys(), "particle type not supported"
            if pdgs[particle] != pdg_id:
                raise Exception("wrong PDG ID! particle_found=%i particle_expected=%i",pdgs[particle],pdg_id)
        except Exception as err:
            del tree, mcprimaries
            raise Exception(err.message)
        return True

def isNull(ptr):
    try:
        heap = ptr.IsOnHeap()
    except ReferenceError:
        return True
    else:
        return False

def getTime(evt):
    if isNull(evt.pEvtHeader()):
        return -1.
    sec = evt.pEvtHeader().GetSecond()
    ms  = evt.pEvtHeader().GetMillisecond()
    time = float("{second}.{ms}".format(second=sec,ms=ms))
    return time

def checkHKD(fname):
    trees = dict( SatStatus = ['DmpHKDSatStatus'],
                     HighVoltage=['DmpHKDHighVoltage'],
                     TempSatellite=['DmpHKDTempSatellite'],
                     TempPayloadNegative=['DmpHKDTempNegative'],
                     TempPayloadPositive=['DmpHKDTempPositive'],
                     CurrentPayloadNegative=['DmpHKDCurrentNegative'],
                     CurrentPayloadPositive=['DmpHKDCurrentPositive'],
                     StatusPayloadNegative=['DmpHKDStatusNegative'],
                     StatusPayloadPositive=['DmpHKDStatusPositive'],
                     StatusPowerSupplyPositive=['DmpHKDStatusPowerSupplyPositive'],
                     StatusPowerSupplyNegative=['DmpHKDStatusPowerSupplyNegative'],
                     PayloadDataProcesser=['DmpHKDPayloadDataProcessor'],
                     PayloadManager=['DmpHKDPayloadManager'])
    try:
        for tree, branches in trees.iteritems():
            ch = TChain("HousekeepingData/{tree}".format(tree=tree))
            ch.Add(fname)
            if ch.GetEntries() == 0: raise Exception("HKD tree %s empty",tree)
            checkBranches(tree, branches)
    except Exception as err:
        raise Exception(err.message)
    return True

def isFlight(fname):
    ch = DmpChain("CollectionTree")
    ch.SetVerbose(0)
    ch.Add(infile)
    nevts = int(ch.GetEntries())
    if not nevts: raise Exception("zero events")
    evt = ch.GetDmpEvent(0)
    tstart = getTime(evt)
    #for i in tqdm(xrange(nevts)):
    #    evt = ch.GetDmpEvent(i)
    #    if i == 0:
    evt = ch.GetDmpEvent(nevts-1)
    tstop = getTime(evt)
    flight_data = True if ch.GetDataType() == DmpChain.kFlight else False
    del ch
    del evt
    return flight_data, dict(tstart=tstart, tstop=tstop)

def getSize(lfn):
    if lfn.startswith("root://"):
        server = "root://{server}".format(server=lfn.split("/")[2])
        xc = client.FileSystem(server)
        is_ok, res = xc.stat(lfn.replace(server,""))
        if not is_ok.ok: raise Exception(is_ok.message)
        return res.size
    else:
        return getsize(lfn)

tstart = -1.
tstop = -1.
fsize = 0.
good = True
comment = "NONE"
f_type = None
try:
    fsize = getSize(infile)
    tch = TChain("CollectionTree")
    tch.Add(infile)
    nevts = int(tch.GetEntries())
    if nevts == 0: raise IOError("zero events.")
    flight_data, stat = isFlight(infile)
    if flight_data:
        good = checkHKD(infile)
        tstart = stat.get("tstart",-1.)
        tstop  = stat.get("tstop",-1.)
        f_type = "2A"
    else:
        #print 'mc data'
        simu_branches = [tch.FindBranch(b) for b in branches['mc:simu']]
        reco_branches = [tch.FindBranch(b) for b in branches['mc:reco']]

        if None in simu_branches:
            f_type = "mc:reco"
            if None in reco_branches: raise Exception("missing branches in mc:reco")
        else:
            f_type = "mc:simu"
        if(testPdgId(infile)): good = True
    if good:
        good = checkBranches(tch, branches[f_type])

except Exception as err:
    comment = str(err)
    good = False

f_out = dict(lfn=infile, nevts=nevts, tstart=tstart, tstop=tstop, good=good,
             comment=comment, size=fsize, type=f_type)

print f_out