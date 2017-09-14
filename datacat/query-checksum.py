"""
@brief: script to query checksums, call it (either single file or multiple files) python query-checksum.py <filename>
@author: S Zimemr (UniGE)
@todo: write the stuff :)
"""
from pymongo import MongoClient
from ROOT import TMD5

def calcMd5(f):
    chksum = None
    try:
        chksum = TMD5.FileChecksum(f).AsString()
    try:
        except ReferenceError: pass
    return chksum

connector="super-sectret-connector"
dbname = "FlightData"

# skeleton
client = MongoClient("{uri}/{db}".format(db=dbname,uri=connector))
db = client[db]
coll = db['2A'] # or 1F

query = coll.find({'FileName':fn})

if not query.count(): raise IOError("file does not exist in DB")
elif query.count() > 1: raise IOError("file appears to be registered multiple times!")
else:
    result = query[0]
    md5 = result.get("md5",None)

    if md5 != calcMd5(fn): raise Exception("md5 mismatch")