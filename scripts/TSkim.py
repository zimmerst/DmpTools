'''
Created on Mar 16, 2016
@author: zimmer
@brief: converts ROOT file pandas (for now), heavily inspired by Fermi's TSkim tool.
'''
#!/usr/bin/env python
import logging
from progress.bar import Bar
import pandas as pd
import numpy as np
from ROOT import TChain, TTreeFormula
from optparse import OptionParser
import os

if __name__ == '__main__':
    
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("--InputFile", dest="inmf", help="Input Data Merit File")
    parser.add_option("--OutputFile", dest="otmf",default='output.pdy', help="Output Merit File")
    parser.add_option("--TCut", dest="cuts",default=None, help="TCut String in Quotes")
    parser.add_option("--TreeName", dest="ttree",default="MeritTuple", help="name of tree to store")
    (options,args)= parser.parse_args()
    logging.info("Input file: %s",options.inmf)
    logging.info("Cut string: %s",options.cuts)
    
    IntBrName = []#'latitude']
    DblBrName = ['latitude','longitude']
    
#    # integer variables
#    IntBrName=['ObfGamState','FswGamState','EvtEventId','FT1EventClass','McSourceId']
#    # double variables
#    DblBrName=['EvtElapsedTime','CTBCPFGamProb','Tkr1ToTTrAve','CalTrSizeTkrT68',
#               'Tkr1KalThetaMS','Tkr1X0','Tkr1Z0','Tkr1ZDir','Tkr1XDir','Tkr1YDir',
#               'Tkr1Y0','FT1Theta','CalTransRms','TkrNumTracks','CalEnergyRaw',
#               'CalLongRms','FT1Energy','CTBBestEnergy','CalTrackAngle','CalTrackDoca','TkrDispersion',
#               'GltGemSummary','CalCsIRLn','CTBBestZDir','CalLRmsAsym','CalTrSizeTkrT95',
#               'Tkr1CoreHC','Tkr1Hits','Tkr1ToTTrAve','CTBBestLogEnergy','AcdTotalEnergy',
#               'AcdTileCount','CTBBestEnergyProb','CalELayer0','CalELayer1','CalELayer2',
#               'CalELayer3','CalELayer4','CalELayer5','CalELayer6','CalELayer7',
#               'AcdTkr1ActiveDist','AcdTkr1ActDistTileEnergy','CalTrSizeTkrT90','CalCfpChiSq',
#               'CTBClassLevel','CTBParticleType','McEnergy','McId','McEarthAzimuth','McZenithTheta','McRa','McDec','McL','McB',
#               'PtLat','PtLon','PtRaz','PtDecz','PtRax','PtDecx','PtAlt','PtMagLat',
#               'PtSCzenith','PtMcIlwainB','PtMcIlwainL',
#               'PtLambda','PtR','PtBEast','PtBNorth','PtBUp',
#               'FT1Ra','FT1Dec','FT1L','FT1B','FT1EarthAzimuth','FT1ZenithTheta','FT1Phi']
    # create pandas dataframe
    allColumns = IntBrName+DblBrName #
    df_ = pd.DataFrame(columns=allColumns)
    IntBrVal=[np.array([0]) for x in IntBrName]
    DblBrVal=[np.array([0.]) for x in DblBrName]
    if os.path.isfile(options.inmf):
        # have inputfile
        files = open(options.inmf,'r').readlines()
        InfileArg = []
        for f in files:
            InfileArg.append(f.replace("\n",""))
    filenum1=0
    nEntTot=0
    logging.info("found %i files",len(InfileArg))
    cube = None
    while filenum1<len(InfileArg):
        ifilename=InfileArg[filenum1]
        MeritIn=TChain(options.ttree)
        MeritIn.Add(ifilename)
        nEnt=MeritIn.GetEntries()
        nEnt = 100000 # debug
        logging.info('found %i events',int(nEnt))
        bar_suffix = "%(percent)d%%- %(elapsed)ds" #'%(percent)d%%'
        bbar = Bar("%s: Progress..."%os.path.basename(ifilename),max=int(nEnt), suffix=bar_suffix)
        if(nEnt==0):
            del MeritIn
            logging.warning("WARNING! EMPTY FILE %s",ifilename)
            filenum1+=1
            continue
        if not options.cuts is None:
            CutEval=TTreeFormula("CutEval",options.cuts,MeritIn)
        #nEntTot+=nEnt
        tmp_frame = pd.DataFrame(index=np.arange(nEnt),columns=allColumns)
        tmp_frame = tmp_frame.fillna(0)
        for i in range(nEnt):
            #if i<100:
            MeritIn.GetEntry(i)
            if not options.cuts is None:
                if(CutEval.EvalInstance(i)==0): continue
        # specifically clone branches
            for j in range(len(IntBrName)):
                IntBrVal[j][0]=getattr(MeritIn,IntBrName[j])
            for j in range(len(DblBrName)):
                DblBrVal[j][0]=getattr(MeritIn,DblBrName[j])
            # this fills the row with all values and appends to existing dataframe
            if len(IntBrVal) and len(DblBrVal):
                series=np.hstack([np.column_stack(IntBrVal),np.column_stack(DblBrVal)])
            else:
                series = np.array(IntBrVal if len(IntBrVal) else DblBrVal).T            
            tmp_frame.loc[i] = series[0]
            del series
            bbar.next()
        df_.append(tmp_frame)
        del tmp_frame
        bbar.finish()
        filenum1+=1
        del MeritIn
        del bbar
        df_.to_pickle(options.otmf) # should save in the end to make sure we store process along the way.

    # dump the pandas dataframe
    # check out: https://metarabbit.wordpress.com/2013/12/10/how-to-save-load-large-pandas-dataframes/comment-page-1/
    df_.to_pickle(options.otmf)
    logging.info("Number of input events: %i",int(nEntTot))
