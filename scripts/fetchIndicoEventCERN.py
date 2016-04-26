"""
@author: S. Zimmer (Geneva)
@brief: convenience script to crawl CERN Indico page and extract all contributions for each event with identical names
"""

import time, datetime, json, urllib, hmac, hashlib
# CERN needs both api-key & api-secret (only persistent requests are setup)
GLOB_API_KEY = ''
GLOB_API_SECRET = ''
GLOB_HOSTNAME= "https://indico.cern.ch"


def contrib2twiki(cdict):
	ret = "   * *%s* - %s"%(cdict['title'],cdict['speaker'])
	if 'slides' in cdict:
		ret+=" [[%s][(slides)]]"%cdict['slides']
	return ret

def IS_OK(ret,msg):
	return {'OK':ret,'Message':msg}

def toTimeStamp(timeJson):
	y,m,d = [int(k) for k in str(timeJson['date']).split("-")]
	H,M,S = [int(k) for k in str(timeJson['time']).split(":")]
	dt = datetime.datetime(y,m,d,H,M,S)
	return time.mktime(dt.timetuple())

def nextMeeting(timeJson):
	''' returns true if next meeting is in future, else false '''
	timeNow = time.mktime(datetime.datetime.now().timetuple())
	timeStamp = toTimeStamp(timeJson)
	if timeStamp >= timeNow:
		return True
	return False

class IndicoObject(object):
	PATH= None
	ID = None
	API_KEY = GLOB_API_KEY
	API_SECRET = GLOB_API_SECRET
	PARAMS = {}
	URL = None
	JSON = None

	def __buildIndicoRequest__(self):
		items = []
		items += self.PARAMS.items()
		items.append(('ak',self.API_KEY))
		items = sorted(items, key=lambda x: x[0].lower())
		path = '%s/%s.json'%(self.PATH,self.ID)
		merged_path = '%s?%s' % (path, urllib.urlencode(items))
		signature = hmac.new(self.API_SECRET, merged_path, hashlib.sha1).hexdigest()
    # remove 0 item
		del items[0]
		items = sorted(items, key=lambda x: x[0].lower())
		items.append(('ak',self.API_KEY))
		merged_path = '%s?%s' % (path, urllib.urlencode(items))
		self.URL = "%s%s&signature=%s"%(GLOB_HOSTNAME,merged_path,signature)
		return self.URL
	
	def __init__(self,**kwargs):
		self.__dict__.update(kwargs)
		self.__setDefaults__()
		self.__buildIndicoRequest__()
	
	def __setDefaults__(self):
		self.PARAMS['limit']='123'
		self.PARAMS['pretty']='yes'
	
	def setObjectId(self,EVENT_ID):
		self.ID=EVENT_ID
	
	def validateJSON(self):
		if self.JSON is None:							return IS_OK(False,'JSON query empty, maybe something went wrong')
		if not len(self.JSON['results']): return IS_OK(False,'JSON query seemingly okay, but results are empty')
		#content = self.JSON['results']
		return IS_OK(True,"Everything is Fine")
	
	def submitQuery(self):
		try:
			f = urllib.urlopen(self.URL)
			raw_data = f.read()
			self.JSON = json.loads(raw_data)
		except IOError, io:
			return IS_OK(False,io)
		return True

class IndicoCategory(IndicoObject):
	PATH = "/export/categ"
	PARAMS ={'detail':'events'}
	
	def getEvents(self,title):
		ret = []
		res = self.validateJSON()
		if not res['OK']:
			print 'error validating JSON, returning an empty list, error below'
			print	res['Message']
			return ret
		for ev in self.JSON['results']:
			if ev['title'] == title:
				ret.append(ev)
		return ret

class IndicoEvent(IndicoObject):
	PATH = "/export/event"
	PARAMS = {'detail':'contributions'}
	
	def getContributions(self,with_material=True):
		''' returns the contributions as list of dictionaries '''
		ret = []
		res = self.validateJSON()
		if not res['OK']:
			print 'error validating JSON, returning an empty list, error below'
			print	res['Message']
			return ret
		contributions = self.JSON['results'][0]['contributions']
		#print 'found %i contributions'%len(contributions)
		for c in contributions:
			#print "processing item %i"%i
			r = {'title':c['title']}
			r['timestamp'] = toTimeStamp(c['startDate'])
			if len(c['speakers']):
				r['speaker']=c['speakers'][0]['fullName']
				if len(c['speakers'][0]['affiliation']):
					r['speaker']+=" (%s)"%c['speakers'][0]['affiliation']
			else: r['speaker']='no speaker'
			if with_material:
				r['slides']=""
				mat = c['material']
				if not len(mat):
					#print 'found no material associated with contribution %s'%r['title']
					continue
				if not len(mat[0]['resources']):
					print 'found material but no resources for %s'%r['title']
					continue
				r['slides']=mat[0]['resources'][0]['url']
			ret.append(r)
		#print ret[-1]
		return sorted(ret, key = lambda user: user['timestamp'])
	
	def getMinutes(self):
		ret = None
		res = self.validateJSON()
		if not res['OK']:
			print 'error validating JSON, returning an empty list, error below'
			print	res['Message']
			return ret
		material = self.JSON['results'][-1]['material'][0] # will always be a list
		if 'id' in material:
			if material['id']=='minutes': ret = material['resources'][-1]['url']
		return ret


if __name__ == '__main__':
	from optparse import OptionParser
	parser = OptionParser()
	usage = "Usage: %prog [options]"
	description = "fetch Indico content from %s"%GLOB_HOSTNAME
	parser.set_usage(usage)
	parser.set_description(description)
	parser.add_option("--title",dest='title',default='DAMPE-EU data analysis',help="title to be used in twiki")
	parser.add_option("--meeting_title",dest='mtitle',default="DAMPE data analysis",help="title of event in Indico")
	(opts, arguments) = parser.parse_args()
	doc_header = "---+ DAMPE %s\n*Do not edit this page manually, as it is created by a bot*"%opts.title
	my_cat = IndicoCategory(ID=7913)
	my_cat.submitQuery()
	events = reversed(my_cat.getEvents(title=opts.mtitle))
	print doc_header
	for i,ev in enumerate(events):
		startDate = ev['startDate']
		h = "---++++ [[%s][%s]]"%(ev['url']," ".join([startDate[key] for key in ['date','time','tz']]))
		if i == 0 and nextMeeting(startDate): h+= " *(next meeting)*"
		print h
		#print ev['title']
		my_event = IndicoEvent(ID=int(ev['id']))
		my_event.submitQuery()
		contribs = my_event.getContributions()
		for c in contribs:
			print contrib2twiki(c)
		minutes = my_event.getMinutes()
		if minutes: print "   * [[%s][Minutes]]"%minutes
	print "\nLast Update: %s"%time.ctime()


