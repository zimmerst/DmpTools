# create bad file list.
from sys import argv
from importlib import import_module
from os.path import splitext, isfile

infile = argv[1]
badfile= argv[2]

ext = splitext(infile)[1]
supported_backends = {".json":"json",".yaml":"yaml",".pkl":"pickle"}
assert ext in supported_backends, "unsupported output format, {f}".format(f=ext)
oout = []
pack = import_module(supported_backends[ext])
# this makes sure to support the various formats.
if isfile(infile):
    my_open = lambda inf : open(inf,'rb').read() if ext == '.yaml' else open(inf,'rb')
    oout = pack.load(my_open(infile))

bad_files = [o['lfn'] for o in oout if not o['good']]
if len(bad_files):
    with open(badfile,'w') as fout:
        fout.write("\n".join(bad_files))
        fout.close()



