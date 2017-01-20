"""

@author: zimmer
@date: 2017-01-19
@comment: a first implementation of a crawler of DAMPE data, depending on DAMPE framework.
@todo: implement livetime calculation.

"""
from sys import argv
from ROOT import gSystem, gROOT
from os.path import getsize
from tqdm import tqdm
gROOT.SetBatch(True)
gROOT.ProcessLine("gErrorIgnoreLevel = 3002;")
from XRootD import client

infile = argv[1]

res = gSystem.Load("libDmpEvent")
if res != 0:
    raise ImportError("could not import libDmpEvent, mission failed.")
from ROOT import TChain, DmpChain

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

def testPdgId(fname,evt):
    pdg_id = int(evt.pEvtSimuPrimaries().pvpart_pdg)
    if pdg_id > 10000:
        pdg_id = int(pdg_id/10000.) - 100000
    from os.path import basename
    bn = basename(evt).split(".")[0].lower()
    if not bn.startswith("all"):
        print 'non-standard sample, skip'
        return
    if "bkg" or "background" in bn:
        print 'background sample, skip'
        return
    pdgs = dict(proton=2212, electron=11, gamma=22,he = 2, li = 3, be = 4, b = 5, c = 6, n = 7, o = 8)
    failed = False
    for pdg in pdgs:
        if pdg in bn:
            if pdg_id != pdg[pdgs]:
                failed = True
            else:
                failed = False
    if failed:
        raise Exception("wrong PDG ID!")
    return

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
            for b in branches:
                r = ch.FindBranch(b)
                assert r is not None, 'missing branch : %s' % b
    except Exception as err:
        raise Exception(err.message)

def getSize(lfn):
    if lfn.startswith("root://"):
        server = "root://{server}".format(server=lfn.split("/")[2])
        xc = client.FileSystem(server)
        is_ok, res = xc.stat(lfn.replace(server,""))
        if not is_ok.ok: raise Exception(is_ok.message)
        return res.size
    else:
        return getsize(lfn)

ch = DmpChain("CollectionTree")
ch.Add(infile)
nevts = int(ch.GetEntries())
tstart = -1.
tstop = -1.
fsize = 0.
good = True
comment = "NONE"
f_type = None
try:
    fsize = getSize(infile)
    if nevts == 0: raise IOError("zero events.")
    else:
        for i in tqdm(xrange(nevts)):
            evt = ch.GetDmpEvent(i)
            flight_data = True if ch.GetDataType() == DmpChain.kFlight else False
            if flight_data:
                if i == 0:
                    tstart = getTime(evt)
        if flight_data:
            tstop = getTime(evt)
            f_type = "2A"
        else:
            # must be simu data or reco
            reco_missing = isNull(evt.pEvtBgoRec())
            simu_missing = isNull(evt.pEvtSimuPrimaries())
            if reco_missing and simu_missing:
                raise Exception("both DmpEvtSimuPrimaries and DmpEvtBgoRec appear missing.")
            elif reco_missing:
                f_type = "mc:simu"
            else:
                f_type = "mc:reco"
            testPdgId(infile,evt)
        del ch
        print 'verification of branches.'
        if flight_data:
            checkHKD(infile)
        tch = TChain("CollectionTree")
        tch.Add(infile)
        for b in branches[f_type]:
            r = tch.FindBranch(b)
            assert r is not None, 'missing branch : %s' % b

except Exception as err:
    comment = err.message
    good = False

f_out = dict(lfn=infile, nevts=nevts, tstart=tstart, tstop=tstop, good=good,
             comment=comment, size=fsize, type=f_type)

print f_out