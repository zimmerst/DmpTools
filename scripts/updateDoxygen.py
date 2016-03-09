'''
Created on Mar 9, 2016

@author: zimmer
@summary: script attempts to connect to svn server, checks out a revision (or trunk) and attempts running doxygen on it

'''
import sys, logging, ConfigParser, os, subprocess, shutil, time, shlex

def mkdir(dir):
    if not os.path.exists(dir):  os.makedirs(dir)
    return dir

def safe_copy(infile, outfile, sleep=10, attempts=10):
    infile = infile.replace("@","") if infile.startswith("@") else infile
    # Try not to step on any toes....
    if infile.startswith("root:"):
        print 'file is on xrootd - switching to XRD library'
        cmnd = "xrdcp %s %s"%(infile,outfile)
    else:
        cmnd = "cp %s %s"%(infile,outfile)
    i = 0
    logging.info("copy %s -> %s"%(infile,outfile))
    while i < attempts: 
        status = subprocess.call(shlex.split(cmnd))
        if status == 0: 
            return status
        else:
            logging.warning("%i - Copy failed; sleep %ss"%(i,sleep))
            time.sleep(sleep)
        i += 1
    raise Exception("File *really* doesn't exist: %s"%infile)

class HTMLDocument(object):
    title = None
    header = None
    HTMLHeader = None
    links = {}
    _body = None
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
    def set_header(self,header):
        logging.debug("setting html header %s"%header)
        self.header = header
    def add_link(self,key,value):
        logging.debug("adding %s: %s"%(key,value))
        self.links[key]=value
    def remove_link(self,key):
        if key in self.links:
            del self.links[key]
    def __compileBody(self):
        my_list = []
        if 'trunk' in self.links:
            my_list += ["\n<h4><a href=\"%s\">trunk</a></h4>"%self.links['trunk']]
            del self.links['trunk']
        my_list += ["\n<h4><a href=\"%s\">%s</a></h4>"%(v,k) for (k,v) in sorted(self.links.iteritems(),-1)]
        html_body = "<body><h1>%s</h1>"%self.title
        html_body+= "".join(my_list)
        html_body+= "\n</body>"
        logging.debug("HTML Body follows \n%s"%html_body)
        return html_body
    def dump(self,outfile):
        foo = open(outfile,'w')
        body = self.__compileBody()
        html_str = "<html><head><title>%s</title>\n%s"%(self.HTMLHeader,body)
        foo.write(html_str)
        foo.close()
            
def init_directory(mydir,exec_path):
    os.chdir(mydir)
    logging.debug("current directory: %s"%os.curdir)
    share_path = os.path.join(exec_path,"../share/doxygen")
    for f in os.listdir(share_path):
        infile = os.path.join(share_path,f)
        outfile= os.path.join(mydir,f)
        safe_copy(os.path.abspath(infile),outfile)

def run(cmd_args):
    if not isinstance(cmd_args, list):
        raise RuntimeError('must be list to be called')
    logging.info("attempting to run: %s"%" ".join(cmd_args))
    proc = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if not err is None:
        for e in err.split("\n"): logging.error(e)
    for d in out.split("\n"):
        logging.debug(d)

if __name__ == '__main__':
    pwd = os.curdir
    from optparse import OptionParser
    parser = OptionParser()
    usage = "Usage: %prog [options] config.cfg"
    description = "script updates doxygen-generated web-pages after updating svn, to be run as cron job"
    parser.set_usage(usage)
    parser.set_description(description)
    parser.add_option("--debug",dest="debug",action="store_true",default=False, help="run in debug mode")
    parser.add_option("--no-cleanup",dest="skip_cleanup",action="store_true",default=False, 
                      help="if set to true, keep the entire source dir, otherwise only Documentation & Examples are kept")
    parser.add_option("--svnrepo",dest='svn_repo',type=str,default=None,help='overrides repository setting in cfg')
    parser.add_option("--tag",dest='svn_tag',type=str,default='trunk',help='tag to checkout')
    parser.add_option("-r","--release",dest='release',action='store_true',default=False,help='if used, assume this is a tagged release')
    parser.add_option("--dest",dest='doxygen_main',type=str,default=None,help="overrides doxygen storage location")
    parser.add_option("--log",dest='logfile',type=str,default=None,help="overrides log-file destination")
    (opts, arguments) = parser.parse_args()
    if len(sys.argv)<1:
        print parser.print_help()
        raise Exception
    exec_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    cfgFile = sys.argv[1]
    configParser = ConfigParser.SafeConfigParser(allow_no_value=True)
    configParser.read(cfgFile)
    cfg = dict(configParser.items("doxygen"))
    _opts = dict((k,v) for (k,v) in vars(opts).iteritems() if not v is None)
    cfg.update(_opts)
    cfg.setdefault('logfile','doxygen.log')
    # set logger
    mkdir(cfg['doxygen_main'])
    logging.basicConfig(filename=cfg['logfile'],level=logging.DEBUG if opts.debug else logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    
    html = HTMLDocument(title="List of DmpSoftware Releases",HTMLHeader="Doxygen Documentation for DmpFramework")
    init_directory(cfg['doxygen_main'],exec_path)
    ## okay, dealt with inputs, now let's do the real stuff
    out_dir = cfg['doxygen_main']+"/trunk" if not opts.release else cfg['doxygen_main']+"/%s"%cfg['svn_tag'] 
    logging.info("executing doxygen magic in %s"%out_dir)
    if os.path.isdir(out_dir):
        logging.info("found output directory already, attempting an update to save time")
        os.chdir(out_dir)
        cmd_args = ['svn update','']
    else:
        co = '/trunk' if not opts.release else '/tags/%s %s'%(cfg['svn_tag'],cfg['svn_tag'])
        cmd_args = ['svn co %s'%(cfg['svn_repo']+co),'']
    os.chdir(cfg['doxygen_main'])
    logging.info("about to execute remote svn command, output suppressed")
    run(cmd_args)
    # next, prepare doxygen stuff
    doc_dir = os.path.join(out_dir,"Documentation")
    if not os.path.isdir(doc_dir):
        logging.error("could not find Documentation directory, this may be the case if you attempt to create the documentation for an older release")
        safe_copy(os.path.join(cfg['doxygen_main'],"doxygen.tar.gz"),os.path.join(out_dir,"doxygen.tar.gz"))
        logging.warning("trying to remedy the situation by adding the default Doxygen configuration, which may be out-dated")
        os.chdir(out_dir)
        run(['tar xzvf doxygen.tar.gz'])
        os.remove('doxygen.tar.gz')
    os.chdir(os.path.join(out_dir,"Documentation"))
    run(["%s do.config"%cfg['doxygen_binary']])
    # next cleanup
    if not opts.skip_cleanup:
        os.chdir(out_dir)
        logging.info("perform cleanup to safe space!")
        for f in os.listdir(out_dir):
            if not f in ['Documentation','Examples']:
                logging.debug("attempting to remove %s"%f)
                if os.path.isfile(f): os.remove(f)
                else: shutil.rmtree(f)
    ## find existing folders
    os.chdir(cfg['doxygen_main'])
    doxygen_loc = "Documentation/html/index.html"
    folders = [f for f in os.listdir('.') if os.path.isdir(f)]
    docs = {key:os.path.join(key,doxygen_loc) for key in folders if os.path.isfile(os.path.join(key,doxygen_loc))}
    logging.info("found %i tags"%len(docs.keys()))
    for key, value in docs.iteritems():
        html.add_link(key,value)
    html.dump("index.html")
    logging.info("created index.html and linked new content")
    os.chdir(pwd)
    logging.info("completed this cycle")