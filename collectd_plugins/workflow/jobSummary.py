#!/opt/virtualenvs/DAMPE/bin/python
from DmpWorkflow.core.models import JobInstance
from datetime import datetime, timedelta
from socket import getfqdn as gethostname  # use full domain name.
from time import mktime, sleep
from os import getenv, environ

def tstamp(dt):
    if not isinstance(dt,datetime): raise Exception("must be datetime object")
    return int(mktime(dt.timetuple()))

environ['PLUGIN_NAME']='workflow'
environ['PLUGIN_TYPE']='counter'

HOSTNAME=getenv("COLLECTD_HOSTNAME",gethostname())
INTERVAL=getenv("COLLECTD_INTERVAL",15)
INTERVAL=120 # enough with this fidelity!

start_run = tstamp(datetime.now())
next_run  = start_run + INTERVAL
timeleft  = INTERVAL

statii = ('New','Submitted',"Running")

while timeleft > 0:
    # do query
    start_run = tstamp(datetime.now())
    next_run = start_run + INTERVAL
    query = JobInstance.objects.filter(status__in=statii).item_frequencies("status")
    md = {key: query.get(key, 0) for key in statii}
    for key,value in md.iteritems():
        val="PUTVAL {host}/{plugin}/{ptype}-JobStatus_{key} {start_run}:{value}".format(
            host=HOSTNAME, plugin=getenv("PLUGIN_NAME"), ptype=getenv("PLUGIN_TYPE"),
            key=key, start_run=start_run, value=value)
        print val

    timeleft = next_run - tstamp(datetime.now())
    sleep(timeleft)


