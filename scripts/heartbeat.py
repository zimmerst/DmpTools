def send_heartbeat(proc,version=None,base_url="http://dampevm6.unige.ch:5000"):
    """ 
        convenience function that sends a heart beat to DB
        arguments: 
          - proc: name of process, e.g. JobFetcher
          - version: None (version of process)
    """
    from requests import post
    from datetime import datetime
    from socket import getfqdn as gethostname # use full domain name.    
    host = gethostname()
    url = "%s/testDB/"%base_url
    dt = datetime.now()
    my_dict = {"hostname":host, "timestamp":dt,"process":proc}
    if version is not None:
        my_dict['version']=version        
    res = post(url, data=my_dict)
    res.raise_for_status()
    res = res.json()
    if res.get("result","nok") != "ok":
        print res.get("error")
    return

