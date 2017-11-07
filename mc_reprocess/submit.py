from sys import argv
from tqdm import tqdm
from yaml import load as yload, dump as ydump
from glob import glob
from os.path import isfile, abspath, basename, dirname, join as opjoin
from re import search as research
from os import environ
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
from os import system
SLURM_PARTITION="mono-shared"

def mkdir(pwd):
    system("mkdir -p {p}".format(p=pwd))

def mc2reco(fi,version="v5r4p0",newpath=""):
    """ converts allGamma-vXrYpZ_100GeV_10TeV-p2.noOrb.740485.mc.root to allGamma-v5r4p0_100GeV_10TeV-p2.noOrb.740485.reco.root"""
    #print '*** DEBUG: file: ',fi
    vtag = research("v\dr\dp\d",fi)
    if vtag is None:
        vtag = research("r\d{4}",fi)
    vtag = vtag.group(0)
    # lastly, replace the path
    if fi.startswith("root:"):
        #print fi
        fi = ("/%s"%fi.split("//")[2])
    fname = basename(fi)
    path = dirname(fi)
    task = basename(path)
    npath = opjoin(newpath,task)
    fout = opjoin(npath,fname)
    fout = fout.replace(".mc",".reco")
    max_occ = 10 # version tag shouldn't be there more than 10 times;
    # if we do not include this criterion, if MC-version == reco version this would yield an infinite loop!
    occ = 0
    while vtag in fout:
        fout = fout.replace(vtag,version)
        occ+=1
        if occ >= max_occ: break
    #print "*** DBG ***: ",fout
    return fout

def make_wrapper(infile,outfile):
    """ creates new wrapper file, expands variables as they are there."""
    lines = open(infile,'r').readlines()
    lines_out = []
    for line in lines:
        var = research("\$\{\D+\}",line)
        tline = line
        if not var is None:
            match = var.group(0)
            key   = ((match.replace("$","")).replace("{","")).replace("}","")
            tline = tline.replace(match,"{KEY}".format(KEY=environ[key]))
        lines_out.append(tline)
    of=open(outfile,'w')
    of.write("".join(lines_out))
    of.close()

def parseMultiDays(md):
    """ computes multiples of days, similar to 1 days, 18:00:00 """
    global SLURM_PARTITION
    if not "days, " in md: return md
    days, rest = md.split("days, ")
    hrs, mins, secs = rest.split(":")
    if int(hrs) > 12: SLURM_PARTITION="parallel"
    out = "%i:%02i:%02i"%(int(hrs)+24.*int(days), int(mins), int(secs))
    return out

cfg = yload(open(argv[1],"rb"))

time_per_job = cfg.get("time_per_job",3600.)
if ":" in str(time_per_job):
    now = datetime(day=1,month=1,year=1900,hour=0,minute=0,second=0)
    dt  = datetime.strptime(str(time_per_job),"%H:%M:%S")
    time_per_job = str(dt-now)
else:
    time_per_job = str(timedelta(seconds=time_per_job))

environ["STIME"]=parseMultiDays(time_per_job)
environ['SLURM_PARTITION'] = SLURM_PARTITION
#print '** DEBUG ** SLURM_PARTITION: ',environ.get("SLURM_PARTITION")
#raise Exception
#print "* DEBUG * STIME: ",environ.get("STIME")
#raise Exception
environ["SMEM"] =cfg.get("mem_per_job","2G")
environ["SWPATH"]=cfg.get("DMPSWSYS","/cvmfs/dampe.cern.ch/rhel6-64/opt/releases/trunk")
g_maxfiles = int(cfg.get("files_per_job",10))

ncycles = 1

version=cfg.get("tag","trunk")

slurm_exec_dir=dirname(abspath(__file__))
environ["SLURM_EXEC_DIR"]=slurm_exec_dir
environ["DLOG"]=cfg.get("log_level","INFO")
wrapper=opjoin(slurm_exec_dir,"submit_slurm.sh")

environ["SCRATCH"]=cfg.get("scratch_dir","${HOME}/scratch")

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
    #files_to_process = tqdm([f for f in files_to_process if not isfile(reco_file(f))])
    _files_to_process = []
    for f in tqdm(files_to_process):
        if not isfile(reco_file(f)): _files_to_process.append(f)
    files_to_process = _files_to_process
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

    #print '*** ENV DUMP ***'
    #system("env | sort")
    new_wrapper = opjoin(wd,"submit_slurm.sh")
    make_wrapper(wrapper,new_wrapper)
    system("sbatch {wrapper}".format(wrapper=new_wrapper))
#### DONE