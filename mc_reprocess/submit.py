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
    #print "*** DBG ***: ",fout
    return fout

cfg = yload(open(argv[1],"rb"))



time_per_job = cfg.get("time_per_job",3600.)
if ":" in time_per_job:
    now = datetime(day=1,month=1,year=1900,hour=0,minute=0,second=0)
    dt  = datetime.strptime(time_per_job,"%H:%M:%S")
    time_per_job = str(dt-now)
else:
    time_per_job = str(timedelta(seconds=time_per_job))

environ["STIME"]=time_per_job
environ["SMEM"] =cfg.get("mem_per_job","2G")
environ["SWPATH"]=cfg.get("DMPSWSYS","/cvmfs/dampe.cern.ch/rhel6-64/opt/releases/trunk")
g_maxfiles = int(cfg.get("files_per_job",10))

ncycles = 1

version=cfg.get("tag","trunk")

slurm_exec_dir=dirname(abspath(__file__))
environ["SLURM_EXEC_DIR"]=slurm_exec_dir
wrapper=opjoin(slurm_exec_dir,"submit_slurm.sh")

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

    reco_file = lambda f : mc2reco(f,version=version,newpath=cfg['outputdir'])
    #files_to_process = [f for f in files_to_process if not isfile(reco_file(f))]
    files_to_process = [f for f in files_to_process if not isfile(reco_file(f))]
    #for f in files_to_process:
    #    fsimu = f
    #    freco = reco_file(f)
    #    flag = isfile(freco)
    #    print '*** '
    #    print 'fsimu {fsimu}'.format(fsimu=fsimu)
    #    print 'freco {freco}'.format(freco=freco)
    #    print 'is_file: ',flag
    #    print '*** '
    #    if not flag:
    #        files.append(fsimu)
    #files_to_process = files
    print 'after check: found %i files to process this cycle.'%len(files_to_process)
    nfiles = len(files_to_process)
    chunks = [files_to_process[x:x+g_maxfiles] for x in xrange(0, len(files_to_process), g_maxfiles)]
    print 'created %i chunks this cycle'%len(chunks)
    for j,ch in enumerate(chunks):
        print '** working on chunk %i, size: %i **'%(j+1,len(ch))
        ofile = opjoin(wd,"chunk_%i.yaml"%(j+1))
        inf_c = ch
        out_c = [reco_file(f) for f in inf_c]
        ydump(dict(zip(inf_c,out_c)),open(ofile,'wb'))
        assert isfile(ofile), "yaml file missing!"
        print 'size of chunk: ',len(out_c)
    max_jobs = int(cfg.get("max_jobs",10))
    nch = len(chunks)
    sarr = "1-{nchunks}%{jobs}".format(nchunks=nch,jobs=max_jobs) if \
            nch > max_jobs else "1-{nchunks}".format(nchunks=nch)
    environ["SARR"]=sarr
    print '*** ENV DUMP ***'
    #system("env | sort")
    system("sbatch {wrapper}".format(wrapper=wrapper))
#### DONE