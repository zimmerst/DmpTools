#!/bin/env python
# will find index.html in each sub-dir and link 'em
# usage: python doxygen2html.py target-dir
from sys import argv
from os.path import basename
from glob import glob

class HTMLDocument(object):
    title = None
    header = None
    HTMLHeader = None
    CSS = '    <!-- adding bootstrap --> \
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" \
    integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous"> \
    <!-- Latest compiled and minified JavaScript --> \
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"  \
    integrity="sha384-0mSbJDEHialfmuBBQP6A4Qrprq5OVfW37PRR3j5ELqxss1yVqOtnepnHVP9aJ7xS" crossorigin="anonymous"></script> \
    <style>.content {padding-top: 80px;}</style>'
    links = {}
    _body = None
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
    def set_header(self,header):
        self.header = header
    def add_link(self,key,value):
        self.links[key]=value
    def remove_link(self,key):
        if key in self.links:
            del self.links[key]
    def __compileBody(self,rev=True):
        my_list = []
        if 'trunk' in self.links:
            my_list += ["\n<h5><a href=\"%s\">trunk</a></h5>"%self.links['trunk']]
            del self.links['trunk']
        my_list += ["\n<h5><a href=\"%s\">%s</a></h5>"%(v,k) for (k,v) in sorted(self.links.iteritems(),reverse=rev)]
        html_body = "<body><h1>%s</h1>"%self.title
        html_body+= "".join(my_list)
        html_body+= "\n</body>"
        return html_body
    def dump(self,outfile,reverse=False):
        foop = open(outfile,'w')
        body = self.__compileBody(rev=reverse)
        html_str = "<html><head><title>%s</title>%s</head>\n%s"%(self.HTMLHeader,self.CSS,body)
        foop.write(html_str)
        foop.close()

if __name__ == '__main__':
    dox_dir=argv[1]
    prefix="http://dpnc.unige.ch/dampe/doxygen"
    html = HTMLDocument(title="List of DmpSoftware Releases",HTMLHeader="Doxygen Documentation for DmpFramework")
    release_index=glob("%s/*/index.html"%dox_dir)
    releases = [basename(r.replace("/index.html","")) for r in release_index]
    for key in sorted(releases):
        value = "%s/%s/index.html"%(prefix,key)
        html.add_link(key,value)

    html.dump("%s/index.html"%dox_dir,reverse=True)