from rootpy.tree import Tree, FloatCol
from rootpy.io import root_open
from numpy import ndenumerate, shape

def np2root(data, column_names, outname="output.root",tname="tree"):
    """
    converts numpy array to ROOT TTree and file.
    :param data: the 2D array containing M variables for N events
    :param column_names: M variables
    :param outname: name of the output root file
    :return:
    """
    fOut = root_open(outname,"RECREATE")
    tree = Tree(tname)
    branches = {col:FloatCol() for col in column_names}
    tree.create_branches(branches)
    rows, cols = shape(data)
    for i in range(0, rows):
        for j in range(0, cols):
            exec("tree.{col} = {val}".format(col=column_names[j], val=data[i,j])) in locals()
        tree.Fill()
    fOut.Write()
    fOut.Close()
    print 'wrote ROOT file {name}'.format(name=outname)


def test():
    print 'running test.'
    o = "/tmp/mytest.root"
    t = "mytree"
    from numpy import vstack, random as rd
    col_names = ["A", "B", "C", "D", "E", "F", "G"]
    data = None
    print '0: generate pseudo data.'
    for i in xrange(1000):
        row = rd.random(len(col_names))
        if i == 0:
            print ' content of first row'
            print row
        if data is None:
            data = row
        else:
            data = vstack((data, row))
    np2root(data, col_names, outname=o, tname=t)
    print '1: re-open ROOT file and show content of event 0'
    from ROOT import TFile
    tf = TFile.Open(o)
    tt = tf.Get(t)
    print '2: content of TTree'
    tt.Print()
    print '3: content of event 0'
    tt.Show(0)
    print 'all done.'

if __name__ == '__main__':
    test()