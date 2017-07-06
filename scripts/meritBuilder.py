# MERIT BUILDER
# @brief: creates flat ntuple (trees) from 2A data
# @todo: add pandas.DataSeries hook to convert MeritTree to DataFrame
# @author: Stephan Zimmer (UNIGE)
# @todo: check landscape.io
#####

from sys import argv
import numpy as np
from glob import glob
from progressbar import ProgressBar, ETA, Percentage, Bar
from ROOT import TTree, TFile, gSystem
from rootpy.tree import Tree, TreeModel, FloatCol, IntCol
gSystem.Load("libDmpEvent.so")
from ROOT import DmpChain, DmpEvent
widgets = [Percentage(), Bar(), ETA()]

class MeritTree(TreeModel):
    # let's start with Psd variables
    PsdNhits       = IntCol()     # NEvtPsdHits 

    # Stk variables: first two tracks
    StkT1NhitsXY     = IntCol()      # track[0].getNhitXY()
    StkT1Chi2Ndf     = FloatCol()    # track[0].getChi2NDOF()
    StkT2NhitsXY     = IntCol()      # track[1].getNhitXY()
    StkT2Chi2Ndf     = FloatCol()    # track[1].getChi2NDOF()

    # Bgo variables: pEvtBgoRec
    BgoTotalEnergy = FloatCol() # GetTotalEnergy
    BgoCore3       = FloatCol() # GetEnergyCore3
    
    
    # combinations
    BgoStkCosAngle = FloatCol() # cos(angle) between Bgo direction & Stk leading track
    
    # MC truth: pEvtSimuPrimaries()
    McEnergy       = FloatCol() # pvpart_ekin
    McPID          = IntCol()   # pvpart_pdg
    
    # LATER!
    # FT1 variables (coordinates)
    #Ft1RA_J2000    = FlaotCol()
    #Ft1Dec_J2000   = FloatCol()
    #Ft1Lat         = FloatCol()
    #Ft1Lon         = FloatCol()
    
#https://root.cern.ch/phpBB3/viewtopic.php?t=17090
    
# run analysis here.
inp = argv[1]
print '* * * reading files in %s ... '%inp
dmpch = DmpChain("CollectionTree")
dmpch.SetOutputDir("skim_data/")
if "*" in inp:
    files = glob(inp)
else:
    files = [inp]
for f in files:
    dmpch.Add(f)

nevts = dmpch.GetEntries()
if not nevts: raise Exception("found 0 events")

pbar = ProgressBar(widgets=widgets, maxval=nevts)
tf = TFile("merit.root","RECREATE")








nHE = nBgoSlopeZero = nSingleTrack = nPileUp = 0



##### DO NOT WRITE BELOW THIS LINE #####
print '* * * found %1.1e events '%float(nevts)
pbar.start()
for i in xrange(nevts):
    keepEvent = False
    pev=dmpch.GetDmpEvent()
    totE = pev.pEvtBgoRec().GetTotalEnergy()
    h_BgoTotalEnergy.Fill(TMath.Log10(totE))
    if (pev.pEvtBgoRec().GetTotalEnergy() > 1e4):
        nHE+=1
        continue
    # remove events with BgoSlope x/ y == 0
    if (pev.pEvtBgoRec().GetSlopeXZ() == 0 and pev.pEvtBgoRec().GetSlopeYZ() == 0):
        nBgoSlopeZero+=1
        continue
    # look at track multiplicity
    h_nStkTracks.Fill(pev.NStkKalmanTrack())
    if pev.NStkKalmanTrack() <= 1:
        nSingleTrack+=1
        continue
    pbar.update(i+1)
    # track matching to Bgo
    xz_bgo = lambda z : pev.pEvtBgoRec().GetSlopeXZ() * z + pev.pEvtBgoRec().GetInterceptXZ()
    yz_bgo = lambda z : pev.pEvtBgoRec().GetSlopeYZ() * z + pev.pEvtBgoRec().GetInterceptYZ()
    # find closest track
    for i in range(pev.NStkKalmanTrack()):
        track = pev.pStkKalmanTrack(i)
        xz_stk_slope = track.getDirection().x()/track.getDirection().z()
        yz_stk_slope = track.getDirection().y()/track.getDirection().z()
        xz_stk = lambda z : xz_stk_slope * z + track.getImpactPoint().x()
        yz_stk = lambda z : yz_stk_slope * z + track.getImpactPoint().y()
        ## project out to -325 mm, pre-Psd ##
        x_stk_psd = xz_stk(-325.)
        y_stk_psd = yz_stk(-325.)
        x_bgo_psd = xz_bgo(-325.)
        y_bgo_psd = yz_bgo(-325.)

        
        
        
        # take geometric distance "DOCA"
        d = pow((x_stk_psd - x_bgo_psd)**2 + (y_stk_psd - y_bgo_psd)**2, 0.5)
        # store DOCA vs chi2/ndf
        h2_chi2_vs_delta.Fill(track.getChi2NDOF(), d)

        # use pile-up candidates
        if (track.getChi2NDOF() <= 30. and d >= 500.):
           keepEvent = True
    if keepEvent:
        dmpch.SaveCurrentEvent()
        nPileUp += 1
pbar.finish()
dmpch.Terminate()
#### CLEANUP & STORING OF OUTPUTS #####
#data.Write()




print 'total events: %e'%float(nevts)
LEcut = float(nevts-nHE)
print 'events with E <= 10 GeV: %e (%1.1f)'%(LEcut,100.*LEcut/float(nevts))
slopeCut = float(nevts-nHE-nBgoSlopeZero)
print 'events with slope XZ/YZ == 0: %e (%1.1f)'%(slopeCut,100.*slopeCut/float(nevts))
trackCut = float(nevts-nHE-nBgoSlopeZero-nSingleTrack)
print 'events with 0 or 1 track: %e (%1.1f)'%(trackCut, 100.*trackCut/float(nevts))
print 'pile-up candidats :%e (%1.1f)'%(float(nPileUp), float(nPileUp)/float(nevts))

# store projections
h2_chi2_vs_delta_px = h2_chi2_vs_delta.ProjectionX()
h2_chi2_vs_delta_py = h2_chi2_vs_delta.ProjectionY()

h2_chi2_vs_delta_profx = h2_chi2_vs_delta.ProfileX()
h2_chi2_vs_delta_profy = h2_chi2_vs_delta.ProfileY()


tf.Write()
tf.Close()
