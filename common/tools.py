#!/usr/bin/env python
import subprocess as sub
import numpy as np
from numpy import sin,arccos,pi
import os, re, time
import numbers
import shlex
import yaml, logging

def makeSafeName(srcname):
    rep = {".":"d","+":"p","-":"n"}
    for key in rep:
        srcname = srcname.replace(key,rep[key])
    return srcname

def pwd():
    # Careful, won't work after a call to os.chdir...
    return os.environ['PWD']

def mkdir(_dir):
    if not os.path.exists(_dir):  os.makedirs(_dir)
    return _dir

def config():
    npconfig()
    mplconfig()
def rm(pwd):
    os.system("rm -rf %s"%pwd)

def mkscratch():
    if os.path.exists('/scratch/'):    
        return(mkdir('/scratch/%s/'%os.environ['USER']))
    elif os.path.exists('/tmp/'):
        return(mkdir('/tmp/%s/'%os.environ['USER']))
    else:
        raise Exception('...')

def mplconfig():
    #try:             mplconfigdir = os.environ['MPLCONFIGDIR']
    #except KeyError: 
    #    if os.path.exists('/scratch'):
    #        mplconfigdir = '/scratch/%s/'%os.environ['USER']
    #    else:
    #        mplconfigdir = '/tmp/%s/'%os.environ['USER']
    mplconfigdir = '/tmp/%s/'%os.environ['USER']
    os.environ['MPLCONFIGDIR'] = mplconfigdir
    os.environ['MATPLOTLIBRC'] = '%s/.matplotlib/'%os.environ['HOME']
    return mkdir(mplconfigdir)

def npconfig():
    np.seterr(all='ignore')

def round_figures(x, n=5):
    """Returns x rounded to n significant figures."""
    if np.asarray(x).ndim == 0: 
        return round(x, int(n - np.ceil(np.nan_to_num(np.log10(abs(x))))))
    else:
        return np.array( [round(_x, int(n - np.ceil(np.nan_to_num(np.log10(abs(_x)))))) for _x in x] )


def isRoman(string):
    pattern = '^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'
    return not (re.search(pattern, string) is None)

def isArabic(string):
    pattern = '^[0-9]'
    return not (re.search(pattern, string) is None)

def isNumeral(string):
    return isRoman(string) or isArabic(string)

isnum = lambda x: isinstance(x, numbers.Real)

def nancut(a, axis=None):
    if len(a.shape) > 1:
        cut = ~np.isnan(np.sum(a,axis=axis))
    else:
        cut = ~np.isnan(a)
    return a[cut]

def isDMFit(string):
    from uw.darkmatter.spectral import DMFitFunction
    l = DMFitFunction.channel_mapping.values()
    return string in [item for sublist in l for item in sublist]

def event_mask(all_events,allowed_events):
    """ Takes unique event identifier
    and compares it to a set of allowed"""
    return np.array( [ x in allowed_events for x in all_events ])

def hms2decimal(hms):
    DEGREE = 360.
    HOUR = 24.
    MINUTE = 60.
    SECOND = 3600.

    if not isinstance(hms,str):
        raise Exception("...")
    
    if 'h' in hms:
        hour,minute,second = np.array(re.split('[hms]',hms))[:3].astype(float)
        #sign = -1 if hour < 0 else 1
        decimal = (hour + minute * 1./MINUTE + second * 1./SECOND)*(DEGREE/HOUR)
    else:
        sign = -1 if hms.startswith('-') else 1
        degree,minute,second = np.array(re.split('[dms]',hms))[:3].astype(float)
        decimal = abs(degree) + minute * 1./MINUTE + second * 1./SECOND
        decimal *= sign

    return decimal



def parse_sleep(sleep):
    MINUTE=60
    HOUR=60*MINUTE
    DAY=24*HOUR
    WEEK=7*DAY
    if isinstance(sleep,float) or isinstance(sleep,int):
        return sleep
    elif isinstance(sleep,str):
        try: return float(sleep)
        except ValueError: pass
        
        if sleep.endswith('s'): return float(sleep.strip('s'))
        elif sleep.endswith('m'): return float(sleep.strip('m'))*MINUTE
        elif sleep.endswith('h'): return float(sleep.strip('h'))*HOUR
        elif sleep.endswith('d'): return float(sleep.strip('d'))*DAY
        elif sleep.endswith('w'): return float(sleep.strip('w'))*WEEK
        else: raise ValueError
    else:
        raise ValueError

def sleep(sleep):
    return time.sleep(parse_sleep(sleep))

def get_resources():
    import resource
    usage=resource.getrusage(resource.RUSAGE_SELF)
    return '''usertime=%s systime=%s mem=%s mb
           '''%(usage[0],usage[1],
                (usage[2]*resource.getpagesize())/1000000.0 )

def safe_copy(infile, outfile, sleep=10, attempts=10):
    infile = infile.replace("@","") if infile.startswith("@") else infile
    # Try not to step on any toes....
    sleep = parse_sleep(sleep)
    if infile.startswith("root:"):
        print 'file is on xrootd - switching to XRD library'
        cmnd = "xrdcp %s %s"%(infile,outfile)
    else:
        cmnd = "cp %s %s"%(infile,outfile)
    i = 0
    logging.info("copy %s -> %s",infile,outfile)
    while i < attempts: 
        status = sub.call(shlex.split(cmnd))
        if status == 0: 
            return status
        else:
            logging.warning("%i - Copy failed; sleep %ss",i,sleep)
            time.sleep(sleep)
        i += 1
    raise Exception("File *really* doesn't exist: %s"%infile)

def yaml_load(filename):
    """ Load a yaml file (use libyaml when available) """
    if not os.path.exists(filename):
        raise Exception('File does not exist: %s'%(filename))
    if hasattr(yaml,'CLoader'):
        Loader = yaml.CLoader
    else: 
        Loader = yaml.Loader

    try:
        ret = yaml.load(open(filename),Loader=Loader)
    except Exception, e:
        logging.exception("found exception in yaml_load %s"%str(e))
        ret = yaml.load(open(filename),Loader=yaml.Loader)
    return ret
    
def yaml_dump(x, filename):    
    """ Dump object to a yaml file (use libyaml when available) 
        x        : output to dump to the file
        filename : output file (can be file-type or path string)
    """
    #    Dumper = yaml.Dumper
    #    if hasattr(yaml,'CDumper'):
    #        Dumper = yaml.CDumper
    if isinstance(filename, basestring):
        out = open(filename,'w')
    elif isinstance(filename, file):
        out = filename
    else:
        raise Exception("Unrecognized file: ",filename)
    out.write( yaml.dump(x) )
    out.close()

def expand_list_arg(args,delimiter=',',argtype=str):

    if args is None: return args    
    elif not isinstance(args,list):
        o = args.split(delimiter)
    else:
        o = []
        for arg in args: o += arg.split(delimiter)

    o = [argtype(t) for t in o]
        
    return o
    
def update_config(infile, outfile, **kwargs):
    config = yaml_load(infile)
    update_dict(config,kwargs,add_new_keys=True)
    yaml_dump(config, outfile)

    #import yaml
    #config = yaml.load(open(infile))
    #config.update(kwargs)
    #out = open(outfile,'w')
    #out.write(yaml.dump(config))
    #out.close()

def update_dict(d0,d1,add_new_keys=False,append=False):
    """Recursively update the contents of python dictionary d0 with
    the contents of python dictionary d1."""

    if d0 is None or d1 is None: return
    
    for k, v in d0.iteritems():

        if not k in d1: continue

        if isinstance(v,dict) and isinstance(d1[k],dict):
            update_dict(d0[k],d1[k],add_new_keys,append)
        elif isinstance(v,list) and isinstance(d1[k],str):
            d0[k] = d1[k].split(',')            
        elif isinstance(v,np.ndarray) and append:
            d0[k] = np.concatenate((v,d1[k]))
        else: d0[k] = d1[k]

    if add_new_keys:
        for k, v in d1.iteritems(): 
            if not k in d0: d0[k] = d1[k]
    
def load_config(defaults,config=None,**kwargs):
    """Create a configuration dictionary.  The defaults tuple is used
    to create a dictionary in which valid key values are predefined.
    The config dictionary and kwargs are then used to update the
    values in the default configuration dictionary."""

    o = {}
    for item in defaults:
        
        item_list = [None,None,'',None,str]
        item_list[:len(item)] = item        
        key, value, comment, groupname, item_type = item_list

        if len(item) == 1:
            raise Exception('Option tuple must have at least one element.')
                    
        if value is None and (item_type == list or item_type == dict):
            value = item_type()
            
        keypath = key.split('.')

        if len(keypath) > 1:
            groupname = keypath[0]
            key = keypath[1]
                    
        if groupname:
            group = o.setdefault(groupname,{})
            group[key] = value
        else:
            o[key] = value
            
    update_dict(o,config)
    update_dict(o,kwargs)

    return o

def tolist(x):
    """ convenience function that takes in a 
        nested structure of lists and dictionaries
        and converts everything to its base objects.
        This is useful for dupming a file to yaml.

        (a) numpy arrays into python lists

            >>> type(tolist(np.asarray(123))) == int
            True
            >>> tolist(np.asarray([1,2,3])) == [1,2,3]
            True

        (b) numpy strings into python strings.

            >>> tolist([np.asarray('cat')])==['cat']
            True

        (c) an ordered dict to a dict

            >>> ordered=OrderedDict(a=1, b=2)
            >>> type(tolist(ordered)) == dict
            True

        (d) converts unicode to regular strings

            >>> type(u'a') == str
            False
            >>> type(tolist(u'a')) == str
            True

        (e) converts numbers & bools in strings to real represntation,
            (i.e. '123' -> 123)

            >>> type(tolist(np.asarray('123'))) == int
            True
            >>> type(tolist('123')) == int
            True
            >>> tolist('False') == False
            True
    """
    if isinstance(x,list):
        return map(tolist,x)
    elif isinstance(x,dict):
        return dict((tolist(k),tolist(v)) for k,v in x.items())
    elif isinstance(x,np.ndarray) or \
            isinstance(x,np.number):
        # note, call tolist again to convert strings of numbers to numbers
        return tolist(x.tolist())
#    elif isinstance(x,PhaseRange):
#        return x.tolist(dense=True)
#    elif isinstance(x,OrderedDict):
#        return dict(x)
    elif isinstance(x,basestring) or isinstance(x,np.str):
        x=str(x) # convert unicode & numpy strings 
        try:
            return int(x)
        except:
            try:
                return float(x)
            except:
                if x == 'True': return True
                elif x == 'False': return False
                else: return x
    else:
        return x

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "Usage: %prog  [options] input"
    description = "python script"
    parser = OptionParser(usage=usage,description=description)
    (opts, args) = parser.parse_args()


