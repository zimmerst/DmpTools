'''
Created on Mar 9, 2016

@author: zimmer
'''
import sys, logging, ConfigParser, os, glob, subprocess, copy
from common.tools import mkdir, safe_copy

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
            my_list += ["\n<h4><a href=\"%s\">trunk</a></h4><br>"%self.links['trunk']]
            del self.links['trunk']
        my_list += ["\n<h4><a href=\"%s\">%s</a></h4><br>"%(k,v) for (k,v) in sorted(self.links.iteritems(),-1)]
        html_body = "<body><h1>%s</h1>"%self.title
        html_body+= "\n".join(my_list)
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
    pwd = os.curdir
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
    proc = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, shell=True)
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
    
    html = HTMLDocument(title="List of DmpSoftware Releases",header="Doxygen Documentation for DmpFramework")
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
    os.chdir(os.path.join(out_dir,"Documentation"))
    #doxygen_cfg_lines = open("do.config",'r').readlines()
    #for l in doxygen_cfg_lines:
    #    if l.startswith("PROJECT_NUMBER"):
    #        l = "PROJECT_NUMBER    = %s"%cfg['svn_tag'] if opts.release else 'trunk'
    #doxygen_cfg = "\n".join(doxygen_cfg_lines)
    #foo = open("do.config",'w')
    #foo.write(doxygen_cfg)
    #foo.close()
    #mkdir("doxygen")
    #logging.info("attempting to find include folders and header files, output suppressed")
    #logging.info("attempting to find all header files, output suppressed")    
    #INCLUDE_DIRECTORIES = " ".join(["../"+y.replace(out_dir+"/","") for x in os.walk(out_dir) for y in glob.glob(os.path.join(x[0], 'include'))])
    #HEADER_FILES = " ".join(["../"+y.replace(out_dir+"/","") for x in os.walk(out_dir) for y in glob.glob(os.path.join(x[0], '*.h'))])
    #os.chdir(os.path.join(out_dir,"doxygen"))
    #logging.debug("includes: %s"%INCLUDE_DIRECTORIES)
    #logging.debug("header files: %s"%HEADER_FILES)    
    #doxygen_cfg = open(os.path.join(cfg['doxygen_main'],'do.config'),'r').read()
    #doxygen_cfg=doxygen_cfg.replace("$DAMPE_INLCUDE_DIRECTORIES",INCLUDE_DIRECTORIES).replace("$DAMPE_HEADER_FILES",HEADER_FILES)
    #foo = open("do.config",'w')
    #foo.write(doxygen_cfg)
    #foo.close()
    #safe_copy("../../doxygen.html_header","doxygen.html_header")
    # we should be able to run doxygen now
    run(["%s do.config"%cfg['doxygen_binary']])
#    ## find existing folders
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