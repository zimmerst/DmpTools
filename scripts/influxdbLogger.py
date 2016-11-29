#!/bin/env python
""" script to handle xrootd call-backs which are inserted into influxdb """
from influxdb import InfluxDBClient
from argparse import ArgumentParser
from pprint import PrettyPrinter
from sys import exit as sys_exit
from traceback import print_exc

def main(args=None):
    usage = "Usage: %(prog)s [options]"
    description = "adding entry to influxdb"
    parser = ArgumentParser(usage=usage, description=description)
    parser.add_argument("--key",dest="key", type=str, default="free", help="type_instance", required=False)
    parser.add_argument("--value",dest="val", type=str, default="0", help="value to store", required=False) 
    parser.add_argument("--tags",dest="tags", type=str, default=None, help="list of tags, separated by ;", required=False) 
    parser.add_argument("--measurement",dest="meas", type=str, default="xrootd_storage_status", help="value to store", required=False) 
    opts = parser.parse_args(args)
    tags = {}
    if not opts.tags is None:
        tags=dict([tuple(val.split("=")) for val in opts.tags.split(";")])
    tags['host'] = 'grid05.unige.ch'
    tags['type_instance'] = opts.key
    val = opts.val
    try:
        val = float(val)
    except TypeError:
        pass
    json_bdy = [
        {
            "measurement" : opts.meas,
            "tags" : tags,
            "fields" : { "value" : val }
        }
        ]
    pp = PrettyPrinter(indent=2)
    client = InfluxDBClient("192.33.218.223",8086,'dampe','dampe2015','xrootd')
    pp.pprint(json_bdy)
    client.create_database('xrootd')
    ret = client.write_points(json_bdy)
    if not ret: 
        try:
            raise Exception("Could not write points to DB")
        except:
            print_exc()
            sys_exit(int(ret))
    
if __name__ == "__main__":
    main()
