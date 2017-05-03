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
            exec("tree.{col} = {val}".format(col=column_names[j], val=data[i,j])) in globals(), locals()
            tree.Fill()
    fOut.Write()
    fOut.Close()
    print 'wrote ROOT file {name}'.format(name=outname)


def test():
    print 'running test.'
    from numpy import vstack, random as rd
    col_names = ["A", "B", "C"]
    data = None
    for i in xrange(1000):
        row = rd.random(len(col_names))
        if i == 0: print row
        if data is None:
            data = row
        else:
            data = vstack((data, row))
    print ' done generating pseudo data '
    np2root(data, col_names, outname="/tmp/mytest.root", tname="mytree")

if __name__ == '__main__':
    test()