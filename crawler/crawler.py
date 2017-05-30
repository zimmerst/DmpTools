"""

@author: zimmer
@date: 2017-01-19
@comment: a first implementation of a crawler of DAMPE data, depending on DAMPE framework.
@todo: implement livetime calculation.
@todo: reduce verbosity (check with Valerio)

"""
from sys import argv
from ROOT import gSystem, gROOT
from os.path import getsize, abspath, isfile, splitext
#from tqdm import tqdm
#HASMONGO=True
gROOT.SetBatch(True)
gROOT.ProcessLine("gErrorIgnoreLevel = 3002;")
from XRootD import client
from XRootD.client.flags import StatInfoFlags
res = gSystem.Load("libDmpEvent")
if res != 0:
    raise ImportError("could not import libDmpEvent, mission failed.")
try:
    from pymongo import MongoClient
except ImportError:
    HASMONGO = False
from ROOT import TMD5, TMath, TH1D
from ROOT import TChain, TString, DmpChain, DmpEvent, DmpRunSimuHeader

from importlib import import_module
from os import getenv
from os.path import basename, dirname
from datetime import datetime

def insertDocuments(mongopath,docs, debug=False):
    site = getenv("EXECUTION_SITE","UNIGE")
    assert HASMONGO, "pymongo not found, DB mode disabled"
    if debug: print 'establishing db connection'
    cl = MongoClient(mongopath)
    if debug: print cl
    db = client.DampeDC2
    coll = db.crawlerFiles
    objs_to_insert = []
    if debug: print '# objects to insert',len(docs)
    if debug: print 'checking if docs already exist in db'
    for doc in docs:
        fname = basename(doc['lfn'])
        checksum = doc['chksum']
        tname = basename(dirname(doc['lfn']))
        query = coll.find({'cheksum':checksum,'fname':fname}).count()
        doc['task']=tname
        doc['site']=site
        doc['filename']=fname
        if not query:
            doc['creation_date']=datetime.now()
            objs_to_insert.append(doc)
    if len(objs_to_insert):
        result = coll.insert_many(objs_to_insert)
        if debug: print 'inserted #docs:',len(result)


error_code = 0
def main(infile, debug=False):
    pdgs = dict(Proton=2212, Electron=11, Muon=13, Gamma=22,He = 2, Li = 3, Be = 4, B = 5, C = 6, N = 7, O = 8)
    chksum = None
    global error_code

    if not infile.startswith("root://"):
        infile = abspath(infile)
        try:
            chksum = TMD5.FileChecksum(infile).AsString()
        except ReferenceError: pass
    DmpChain.SetVerbose(-1)
    DmpEvent.SetVerbosity(-1)
    if debug:
        DmpChain.SetVerbose(1)
        DmpEvent.SetVerbosity(1)
    types = ("mc:simu","mc:reco","2A")

    branches = {
        "mc:simu":['EventHeader', 'DmpSimuStkHitsCollection', 'DmpSimuPsdHits', 'DmpSimuNudHits0Collection',
                   'DmpSimuNudHits1Collection', 'DmpSimuNudHits2Collection', 'DmpSimuNudHits3Collection',
                   'DmpBgoSptStruct', 'DmpSimuBgoHits', 'DmpEvtSimuHeader', 'DmpEvtSimuPrimaries',
                   'DmpTruthTrajectoriesCollection', 'DmpSimuSeondaryVtxCollection', 'DmpEvtOrbit'],
        "mc:reco":['StkKalmanTracks', 'DmpEvtBgoHits', 'DmpEvtBgoRec', 'EventHeader',
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
        global error_code
        if debug: print 'checking branches.'
        for b in branches:
            res = tree.FindBranch(b)
            if res is None:
                error_code = 1001
                raise Exception("missing branch %s",b)
        return True

    def verifyEnergyBounds(fname,emin,emax):
        if debug: print 'verify energy range from DmpRunSimuHeader'
        ch = TChain("CollectionTree")
        ch.Add(fname)
        nentries = ch.GetEntries()
        h1 = TH1D("h1","hEnergy",10,TMath.Log10(emin),TMath.Log10(emax))
        ch.Project("h1","TMath::Log10(DmpEvtSimuPrimaries.pvpart_ekin)")
        underflow = h1.GetBinContent(0)
        overflow  = h1.GetBinContent(11)
        assert (underflow == 0), "{n} events found below emin={emin} MeV".format(n=int(underflow),emin=emin)
        assert (overflow == 0), "{n} events found above emax={emax} MeV".format(n=int(overflow),emax=emax)
        del h1
        del ch

    def testPdgId(fname):
        global error_code
        if debug: print 'testing for PDG id'
        from os.path import basename
        bn = basename(fname).split(".")[0].split("-")[0]
        if (not bn.startswith("all")) or (("bkg" or "background" or "back") in bn.lower()):
            return True
        else:
            try:
                particle = bn.replace("all","")
                assert particle in pdgs.keys(), "particle type not supported"
                part = pdgs[particle]
                ch = TChain("CollectionTree")
                ch.Add(fname)
                h1 = TH1D("h1","hPdgId",10,part-5,part+5)
                if part < 10:
                    if debug: print 'Ion mode, subtract'
                    ch.Project("h1","TMath::Floor(DmpEvtSimuPrimaries.pvpart_pdg/10000.) - 100000")
                else:
                    ch.Project("h1","DmpEvtSimuPrimaries.pvpart_pdg")
                delta = TMath.Abs(part - h1.GetMean())
                width = h1.GetRMS()
                if width > 0.1: raise ValueError("pdg Id verification failed, distribution too broad, expect delta")
                if delta > 0.1: raise ValueError("pdg Id verification failed, distribution not centered on %i but on %1.1f"%(part,h1.GetMean()))
                if debug:
                    print "Pdg Hist: Mean = {mean}, RMS = {rms}".format(mean=h1.GetMean(), rms=h1.GetRMS())
                del h1
                del ch
            except Exception as err:
                error_code = 1003
                raise Exception(err.message)
            return True

    def isNull(ptr):
        if debug: print 'test if pointer is null.'
        try:
            heap = ptr.IsOnHeap()
        except ReferenceError:
            return True
        else:
            return False

    def getTime(evt):
        if debug: print 'extract timestamp'
        if isNull(evt.pEvtHeader()):
            return -1.
        sec = evt.pEvtHeader().GetSecond()
        ms  = evt.pEvtHeader().GetMillisecond()
        time = float("{second}.{ms}".format(second=sec,ms=ms))
        return time

    def checkHKD(fname):
        global error_code
        if debug: print 'check HKD trees'
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
                if ch.GetEntries() == 0:
                    raise Exception("HKD tree %s empty",tree)
                checkBranches(ch, branches)
        except Exception as err:
            error_code = 1002
            raise Exception(err.message)
        return True

    def extractVersion(fname):
        if debug: print 'extract version'
        ch = TChain("RunMetadataTree")
        ch.Add(fname)
        ch.SetBranchStatus("*",1)
        svn_rev = TString()
        tag = TString()
        ch.SetBranchAddress("SvnRev",svn_rev)
        ch.SetBranchAddress("tag",tag)
        ch.GetEntry(0)
        return str(tag), str(svn_rev)

    def extractEnergyBounds(fname):
        if debug: print 'extract energy boundaries'
        ch = TChain("RunMetadataTree")
        ch.Add(fname)
        simuHeader = DmpRunSimuHeader()
        b_sH = ch.GetBranch("DmpRunSimuHeader")
        ch.SetBranchAddress("DmpRunSimuHeader",simuHeader)
        b_sH.GetEntry(0)
        return simuHeader.GetMinEne(), simuHeader.GetMaxEne()

    def isFlight(fname):
        if debug: print 'check if data is flight data'
        ch = DmpChain("CollectionTree")
        ch.Add(infile)
        nevts = int(ch.GetEntries())
        if not nevts:
            error_code = 1004
            raise Exception("zero events")
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
        global error_code
        if debug: 'print extracting file size'
        if lfn.startswith("root://"):
            server = "root://{server}".format(server=lfn.split("/")[2])
            xc = client.FileSystem(server)
            is_ok, res = xc.stat(lfn.replace(server,""))
            if not is_ok.ok:
                error_code = 2000
                raise Exception(is_ok.message)
            return res.size
        else:
            return getsize(lfn)

    def isFile(lfn):
        global error_code
        if debug: 'print checking file access'
        if debug: print "LFN: ", lfn
        if lfn.startswith("root://"):
            server = "root://{server}".format(server=lfn.split("/")[2])
            if debug: print "server: ", server
            xc = client.FileSystem(server)
            fname = lfn.replace(server, "")
            if debug: print "LFN: ", fname
            if debug: print xc.stat(fname)
            is_ok, res = xc.stat(fname)
            if debug:
                print 'is_ok: ', is_ok
                print 'res: ', res
            if not is_ok.ok:
                error_code = 2000
                raise Exception(is_ok.message)
            if debug:
                print "res.flags: ", res.flags
                print "StatInfoFlags.IS_READABLE: ", StatInfoFlags.IS_READABLE
            if res.flags == 0:
                if debug: print '[!] FIXME: XRootD.client.FileSystem.stat() returned StatInfoFlags = 0, this flag is not supported'
                res.flags = StatInfoFlags.IS_READABLE
            return True if res.flags >= StatInfoFlags.IS_READABLE else False
        else:
            return isfile(lfn)

    tstart = -1.
    tstop = -1.
    fsize = 0.
    good = True
    eMax = -1.
    eMin = -1.
    comment = "NONE"
    f_type = "Other"
    svn_rev = "None"
    tag = "None"
    nevts = 0
    try:
        good = isFile(infile)
        if not good:
            error_code = 2000
            raise Exception("could not access file")

        fsize = getSize(infile)
        tag, svn_rev = extractVersion(infile)
        tch = TChain("CollectionTree")
        tch.Add(infile)
        nevts = int(tch.GetEntries())
        if nevts == 0:
            error_code = 1004
            good = False
            raise IOError("zero events.")
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
                if None in reco_branches:
                    error_code = 1001
                    good = False
                    raise Exception("missing branches in mc:reco")
            else:
                f_type = "mc:simu"
            if(testPdgId(infile)): good = True
            eMin, eMax = extractEnergyBounds(infile)
            if eMin != eMax:
                try:
                    verifyEnergyBounds(infile,eMin,eMax)
                except AssertionError as msg:
                    error_code = 1005
                    raise Exception(msg.Message)
        if good:
            assert f_type in types, "found non-supported dataset type!"
            good = checkBranches(tch, branches[f_type])

    except Exception as err:
        comment = str(err.message)
        good = False

    f_out = dict(lfn=infile, nevts=nevts, tstart=tstart, tstop=tstop, good=good, error_code = error_code,
                 comment=comment, size=fsize, type=f_type, version=tag, SvnRev=svn_rev, emax=eMax, emin=eMin,
                 checksum=chksum)
    return f_out

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    usage = "Usage: %prog [options]"
    description = "extract metadata from root files."
    parser.set_usage(usage)
    parser.set_description(description)
    parser.add_option("--outType","-T",dest='outType',default='FILE',choices=['STDOUT','DB','FILE'],
                      help='output, defaults to FILE')
    parser.add_option("--output","-o",dest='output',default='STDOUT',help='output, defaults to STDOUT')
    parser.add_option("--db",dest='dbpath',default=None,help='name of mongodb if outType==DB')
    parser.add_option("--ftype",dest="ftype",default='mc',choices=['mc','flight'],
                      help='type of data, will go into separate collections if in DB mode')
    parser.add_option("--debug",dest="debug",action="store_true",default=False, help="run in debug mode")
    parser.add_option("--bulk","-b",dest="bulk",action="store_true",
                      default=False,
                      help="run in bulk mode, here it is assumed that the input file is a qualified list of files")
    (opts, arguments) = parser.parse_args()
    out = []
    if opts.bulk:
        out = [main(f.replace("\n",""), opts.debug) for f in open(argv[1],'r').readlines()]
    else:
        out = [main(argv[1], opts.debug)]
    for pack in out:
        if pack['comment'] == 'problem in C++; program state has been reset':
            pack['error_code'] = 3000
            pack['good'] = False
    if opts.outType == 'STDOUT' or opts.output == 'STDOUT':
        print out
    elif opts.outType == "DB":
        insertDocuments(opts.dbpath,out)
    elif opts.outType == "FILE":
        ext = splitext(opts.output)[1]
        supported_backends = {".json":"json",".yaml":"yaml",".pkl":"pickle"}
        assert ext in supported_backends, "unsupported output format, {f}".format(f=ext)
        oout = []
        pack = import_module(supported_backends[ext])
        # this makes sure to support the various formats.
        if isfile(opts.output):
            my_open = lambda inf : open(inf,'rb').read() if ext == '.yaml' else open(inf,'rb')
            oout = pack.load(my_open(opts.output))
        for fpack in out:
            oout.append(fpack)
        pack.dump(oout, open(opts.output, 'wb'))
    else: raise NotSupportedError("not supported type")
