"""
@author: A. Tykhonov (UniGE)
@author: S. Zimmer (UniGE)
"""

from ROOT import TFile, TTree
import sys

def get_branch_size(b):
	result = 0
	l = b.GetListOfBranches()
	for i in xrange(l.GetLast()+1):
		sub = l.At(i)
		result+= sub.GetTotalSize()
	return result * 1.0 

f=TFile(sys.argv[1],"READ")

trees = ['CollectionTree','RunMetadataTree']
for tree in trees:
	t=f.Get(tree)
	branchnames = map(lambda branch: branch.GetName(), t.GetListOfBranches())
	
	MB = 1e6
	GB = 1e9
	zipbytes = t.GetZipBytes() # returns compressed size.
	
	names = {}
	sizes = {}
	for b in branchnames:
		branch = t.GetBranch(b)
		if b in names.keys():
			names[b] += 1
			#print "names[b]=", names[b]
			continue
		s = get_branch_size(branch) 
		names[b] = 1
		sizes[b] = s
	
	print "tree %s"%tree
	print "Collection                       Size (MB)    #duplication of data (factor)"
	for b in names.keys():
		#s = branch.GetTotBytes()
		#s = branch.GetBasketBytes()
		#s = branch.GetTotalSize()
		#print "%30s   %10f"%(b,s)
		#print s
		print "%30s  % 10.5f   %3d"%(b,sizes[b]/MB,names[b])
	totalSize = sum(sizes.values())
	cf = totalSize / zipbytes
	print 'total: %1.2f MB  compressed: %1.2f MB (tree compression factor: %1.2f)'%(totalSize/MB,zipbytes/MB,cf)
