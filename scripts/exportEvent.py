# simple script to export event by #id

from sys import argv
from os.path import abspath
from ROOT import gSystem, gROOT
from os.path import getsize, abspath, isfile, splitext
#from tqdm import tqdm
gROOT.SetBatch(True)
gROOT.ProcessLine("gErrorIgnoreLevel = 3002;")
res = gSystem.Load("libDmpEvent")
if res != 0:
    raise ImportError("could not import libDmpEvent, mission failed.")
from ROOT import DmpChain

infile=argv[1]
ev_id = argv[2]
event_id = []
if "," in ev_id: event_id = tuple([int(e) for e in ev_id.split(",")])
else:
    event_id = tuple([int(ev_id)])

ch = DmpChain("CollectionTree")
ch.SetOutputDir(abspath("."))
ch.Add(infile)

nevts = ch.GetEntries()
if not nevts: raise Exception("no events found in file.")
if max(event_id) > nevts: raise Exception("Event ID > total number of events.")

for i in event_id:
    print 'getting event %i'%i
    pev = ch.GetDmpEvent(i)
    ev_no = pev.pEvtSimuHeader().GetEventNuber()
    print i, ev_no
    ch.SaveCurrentEvent()
ch.Terminate()