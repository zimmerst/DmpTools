from sys import argv
from yaml import load as yload, dump as ydump
from glob import glob
from os.path import isfile, abspath, basename, dirname, join as opjoin
from re import search as research
from os import environ
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
from os import system

def mkdir(pwd):
    system("mkdir -p {p}".format(p=pwd))

def mc2reco(fi,version="v5r4p0",newpath=""):
    """ converts allGamma-vXrYpZ_100GeV_10TeV-p2.noOrb.740485.mc.root to allGamma-v5r4p0_100GeV_10TeV-p2.noOrb.740485.reco.root"""
    #print '*** DEBUG: file: ',fi
    vtag = research("v\dr\dp\d",fi).group(0)
    # lastly, replace the path
    if fi.startswith("root:"):
        fi = ("/%s"%fi.split("//")[2])
    fname = basename(fi)
    path = dirname(fi)
    task = basename(path)
    npath = opjoin(newpath,task)
    fout = opjoin(npath,fname)
    fout = fout.replace(".mc",".reco")
    while vtag in fout:
        fout = fout.replace(vtag,version)
    return fout

cfg = yload(open(argv[1],"rb"))


environ["STIME"]=str( timedelta(seconds=int(cfg.get("time_per_job","3600.") ) ) )
environ["SMEM"] =cfg.get("mem_per_job","2G")
environ["SWPATH"]=cfg.get("DMPSWSYS","/cvmfs/dampe.cern.ch/rhel6-64/opt/releases/trunk")
g_maxfiles = cfg.get("files_per_job")

ncycles = 1

version=cfg.get("tag","trunk")


### LOOP OVER CYCLES ####
for i in xrange(ncycles):
    print '++++ CYCLE %i ++++'%i
    txtfiles = []
    for _d in cfg['inputloc']:
        txtfiles+=glob(_d)

    files_to_process = []
    for t in txtfiles:
        print 'reading %s...'%t
        files_to_process+=[f.replace("\n","") for f in open(t,"r").readlines()]
        print 'size: ',len(files_to_process)
    wd=opjoin(cfg['workdir'],cfg['tag'])
    wd=opjoin(wd,"cycle_%i"%(i+1))
    environ["WORKDIR"]=abspath(wd)
    mkdir(wd)
    print '%i: found %i files to process this cycle.'%(i+1, len(files_to_process))
    print 'check if files exist already'
    files_to_process = [f for f in files_to_process if not isfile(mc2reco(f,version=version,newpath=cfg['outputdir']))]
    print 'after check: found %i files to process this cycle.'%len(files_to_process)
    nfiles = len(files_to_process)
    chunks = []
    ### assemble chunks
    while len(chunks) >= 0:
        ### this is the chunk now
        nfiles = len(files_to_process)
        if not(nfiles): break
        inf_c = out_c = []
        if nfiles <= g_maxfiles:
            inf_c = files_to_process
        else:
            inf_c = [files_to_process.pop(0) for j in xrange(g_maxfiles)]
        chunks.append(inf_c)
        print 'added chunk'
    print 'created %i chunks this cycle'%len(chunks)
    for j,ch in enumerate(chunks):
        print '** working on chunk %i **'
        ofile = opjoin(wd,"chunk_%i.yaml"%j+1)
        inf_c = ch
        for fi in inf_c:
            if fi.startswith("root:"):
                fi = ("/%s"%fi.split("//")[2])
            path = dirname(fi)
            task= basename(path) # makes sure to keep the task
            opath= opjoin(cfg['outputdir'],task)
            out_c= [opjoin(opath,mc2reco(basename(f),version=cfg['tag'])) for f in inf_c]
            ydump(dict(zip(inf_c,out_c)),open(ofile,'wb'))
            assert isfile(ofile), "yaml file missing!"
            print 'size of chunk: ',len(out_c)

    environ["SARR"]="1-{nchunks}%{jobs}".format(nchunks=chunk+1,jobs=int(cfg.get("max_jobs",10)))
    print '*** ENV DUMP ***'
    system("env | sort")
#### DONE