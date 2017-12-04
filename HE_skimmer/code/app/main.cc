/*
    original author: R. Asfandiyarov, UniGE
    modifications: S. Zimmer, UniGE
    history:
    20170712: initial commit to GitHub
    20171009: bugfixes
    20171017: adding dummy photon filter
    20171018: add Maria's v4 of photon selection
    20171020: re-remove Xtrl>150 cut.
    20171104: revised Maria's photon filter: removed E>100 GeV & e3/etot=0.9 constraints
    20171104: added photon2 - place holder for new photon skim.
*/

//@@ C++ includes
#include <sstream>
#include <utility>
#include <fstream>
#include <iostream>
#include <algorithm>
#include <string>
#include <vector>
#include <stdio.h>
using namespace std;

//@@ DMPSW includes
#include "DmpEvtBgoHits.h"
#include "DmpEvtBgoRec.h"
#include "DmpRootEvent.h"
#include "DmpChain.h"

//@@ ROOT includes
#include <TROOT.h>
#include <TSystem.h>
#include <TFile.h>
#include <TTree.h>
#include <TClonesArray.h>
#include <TChain.h>
#include <TBranch.h>
#include <TDirectory.h>
#include <TMath.h>

double Ecore3(DmpEvtBgoRec *bgorec){
    // compute Ecore3 according to Maria's definition
    double elayer[14],core3_me[14],num_bar[14],max_bar[14];
    double maxelayer=-5,num_maxlayer=-5;
    for(int k=0; k<14; k++){
        elayer[k]=-5;
        core3_me[k]=-5;
        num_bar[k]=-5;
        max_bar[k]=-5;
    }
    for(int k=0; k<14; k++){
        elayer[k]=bgorec->GetELayer(k);
        if(elayer[k]<1) elayer[k]=-5;//insert a minumum energy cut to avoid probelms with defauls values set ot zero
    }
    for(int j=0; j<14; j++){
        if(elayer[j]==-5) continue;//if the value was zero so everything stay with the -5 value;
        if(elayer[j]>=maxelayer)
        {
            maxelayer=elayer[j];
            num_maxlayer=j;
        }
        max_bar[j]=bgorec->GetELayerMaxBar(j);

        for(int l=0;l<22;l++)
        {
            if(max_bar[j]==bgorec->GetEdep(j,l)) num_bar[j]=l;
        }
    }

    //if(num_maxlayer>4) continue;
    //calculation of core3 -> Still considering the events that are located in the  extreme bars i think with this I could recover events that are lost in the corners
    double core_f=0;
    for(int z =0 ; z<14; z++){
        core3_me[z]=bgorec->GetEdep(z,num_bar[z]);
        if(num_bar[z]==0){
            core3_me[z]+=bgorec->GetEdep(z,num_bar[z]+1);
        }
        else if (num_bar[z]==21){
            core3_me[z]+=bgorec->GetEdep(z,num_bar[z]-1);
        }
        else if (num_bar[z]>0||num_bar[z]<21){
            core3_me[z]+=bgorec->GetEdep(z,num_bar[z]-1)+bgorec->GetEdep(z,num_bar[z]+1);
        }
        core_f+=core3_me[z];
    }
    return core_f;

}


bool photon_filter(DmpEvent *pev){
    DmpEvtBgoRec* prec = pev->pEvtBgoRec();
    // will return true for any event that passes the photon filter
    double etot = prec->GetTotalEnergy();
    double slope_xz = prec->GetSlopeXZ();
    double slope_yz = prec->GetSlopeYZ();
    double intercept_xz = prec->GetInterceptXZ();
    double intercept_yz = prec->GetInterceptYZ();
    double e3 = Ecore3(prec);
    // position of fiducial volume cut
    double z1 = -298.5;
    double z2 = -324.7;
    double traj_xz = slope_xz * z1 + intercept_xz;
    double traj_yz = slope_yz * z2 + intercept_yz;
    // fiducial volume cut
    if ( (TMath::Abs(traj_xz) > 420.) || (TMath::Abs(traj_yz) > 420.) ) return false;
    // energy cut
    if ( (etot < 1e3) ) return false;
    // finally the E3 core cut
    if (e3/etot < 0.9) return false;
    return true;
}

bool photon_filter2(DmpEvent *pev){
    return false;
}

int main(int argc, char **argv)
{
    long int first_event = atoi(argv[1]);
    long int last_event = atoi(argv[2]);
    int verbosity = atoi(argv[3]);
    TString datafilelist_name = TString::Format("%s",argv[4]);
    long int first_file = atoi(argv[5]);
    long int last_file = atoi(argv[6]);
    int apply_cut= atoi(argv[7]);

    TChain *t_in = new TChain("CollectionTree");
    DmpChain *ch_in= new DmpChain("CollectionTree");
    TChain *rm_in = new TChain("RunMetadataTree");

    const int n_hk_in = 13;
    TChain *hk_in[n_hk_in];
    hk_in[0] = new TChain("HousekeepingData/SatStatus");
    hk_in[1] = new TChain("HousekeepingData/HighVoltage");
    hk_in[2] = new TChain("HousekeepingData/TempSatellite");
    hk_in[3] = new TChain("HousekeepingData/TempPayloadNegative");
    hk_in[4] = new TChain("HousekeepingData/TempPayloadPositive");
    hk_in[5] = new TChain("HousekeepingData/CurrentPayloadNegative");
    hk_in[6] = new TChain("HousekeepingData/CurrentPayloadPositive");
    hk_in[7] = new TChain("HousekeepingData/StatusPayloadNegative");
    hk_in[8] = new TChain("HousekeepingData/StatusPayloadPositive");
    hk_in[9] = new TChain("HousekeepingData/StatusPowerSupplyNegative");
    hk_in[10] = new TChain("HousekeepingData/StatusPowerSupplyPositive");
    hk_in[11] = new TChain("HousekeepingData/PayloadDataProcesser");
    hk_in[12] = new TChain("HousekeepingData/PayloadManager");
    ifstream datafilelist_file(datafilelist_name.Data());
    if (last_file==-1) last_file=2147483646;
    if (datafilelist_file.is_open()) {
        printf("\n%s found\n",datafilelist_name.Data());
        string line;
        long int file_id = 1;
        long int files_added = 0;
        while ( getline (datafilelist_file,line) ){
            if (file_id >= first_file && file_id <= last_file ) {
                if (line.find("dmp")!=std::string::npos) line = "root://grid05.unige.ch:1094" + line;
                t_in->Add(line.data());
                rm_in->Add(line.data());
                ch_in->Add(line.data());
                for (int i=0; i<n_hk_in; i++) hk_in[i]->Add(line.data());
                files_added++;
                printf("Add %s to TChains\n",line.data());
            }
            file_id++; }
        datafilelist_file.close();
        printf("\n%ld file(s) added to TChain\n",files_added);
    } else {
        printf("\n%s not found\n\n",datafilelist_name.Data());
        return 0;}
    long int nevents = t_in->GetEntries();
    if (last_event>nevents || last_event==-1) last_event=nevents-1;
    printf("Total number of events: %ld\n", nevents);
    printf("Process %ld event(s):\n",last_event-first_event+1);

    //@ progress log file
    FILE *logfile = fopen("progress.log","a");
    fprintf(logfile,"Process %ld event(s):\n",last_event-first_event+1);
    fclose(logfile);

    //@ Create output data file
    TFile* f_out_data_002_010 = new TFile("data_002_010.root","RECREATE"); TDirectory* f_out_data_002_010_dir = gDirectory; TTree* t_out_data_002_010 = t_in->CloneTree(0); TTree* hk_out_data_002_010[n_hk_in]; for (int i=0; i<n_hk_in; i++) hk_out_data_002_010[i] = hk_in[i]->CloneTree(0); TTree* rm_out_data_002_010 = rm_in->CloneTree(0);
    TFile* f_out_data_010_025 = new TFile("data_010_025.root","RECREATE"); TDirectory* f_out_data_010_025_dir = gDirectory; TTree* t_out_data_010_025 = t_in->CloneTree(0); TTree* hk_out_data_010_025[n_hk_in]; for (int i=0; i<n_hk_in; i++) hk_out_data_010_025[i] = hk_in[i]->CloneTree(0); TTree* rm_out_data_010_025 = rm_in->CloneTree(0);
    TFile* f_out_data_025_050 = new TFile("data_025_050.root","RECREATE"); TDirectory* f_out_data_025_050_dir = gDirectory; TTree* t_out_data_025_050 = t_in->CloneTree(0); TTree* hk_out_data_025_050[n_hk_in]; for (int i=0; i<n_hk_in; i++) hk_out_data_025_050[i] = hk_in[i]->CloneTree(0); TTree* rm_out_data_025_050 = rm_in->CloneTree(0);
    TFile* f_out_data_050_100 = new TFile("data_050_100.root","RECREATE"); TDirectory* f_out_data_050_100_dir = gDirectory; TTree* t_out_data_050_100 = t_in->CloneTree(0); TTree* hk_out_data_050_100[n_hk_in]; for (int i=0; i<n_hk_in; i++) hk_out_data_050_100[i] = hk_in[i]->CloneTree(0); TTree* rm_out_data_050_100 = rm_in->CloneTree(0);
    TFile* f_out_data_100_500 = new TFile("data_100_500.root","RECREATE"); TDirectory* f_out_data_100_500_dir = gDirectory; TTree* t_out_data_100_500 = t_in->CloneTree(0); TTree* hk_out_data_100_500[n_hk_in]; for (int i=0; i<n_hk_in; i++) hk_out_data_100_500[i] = hk_in[i]->CloneTree(0); TTree* rm_out_data_100_500 = rm_in->CloneTree(0);
    TFile* f_out_data_500_000 = new TFile("data_500_000.root","RECREATE"); TDirectory* f_out_data_500_000_dir = gDirectory; TTree* t_out_data_500_000 = t_in->CloneTree(0); TTree* hk_out_data_500_000[n_hk_in]; for (int i=0; i<n_hk_in; i++) hk_out_data_500_000[i] = hk_in[i]->CloneTree(0); TTree* rm_out_data_500_000 = rm_in->CloneTree(0);
    TFile* f_out_data_photon = new TFile("data_photon.root","RECREATE"); TDirectory* f_out_data_photon_dir = gDirectory; TTree* t_out_data_photon = t_in->CloneTree(0); TTree* hk_out_data_photon[n_hk_in]; for (int i=0; i<n_hk_in; i++) hk_out_data_photon[i] = hk_in[i]->CloneTree(0); TTree* rm_out_data_photon = rm_in->CloneTree(0);
// UNCOMMENT FOR NEW STREAM
//    TFile* f_out_data_photon2 = new TFile("data_photon2.root","RECREATE"); TDirectory* f_out_data_photon2_dir = gDirectory; TTree* t_out_data_photon2 = t_in->CloneTree(0); TTree* hk_out_data_photon2[n_hk_in]; for (int i=0; i<n_hk_in; i++) hk_out_data_photon2[i] = hk_in[i]->CloneTree(0); TTree* rm_out_data_photon2 = rm_in->CloneTree(0);
    DmpEvent *pev = DmpEvent::GetHead(); //ch_in->GetDmpEvent(0);
    DmpEvtBgoHits* bgohits = new DmpEvtBgoHits();
    t_in->SetBranchAddress("DmpEvtBgoHits", &bgohits);
    DmpEvtBgoRec* bgorec = new DmpEvtBgoRec();
    t_in->SetBranchAddress("DmpEvtBgoRec", &bgorec);

    long int time_start = 0;
    long int time_finish = 0;
    int event_local = -1;
    bool rm_filled = false;
    bool pass_photon= false;
    bool pass_event = false;
    bool pass_photon2= false;
    //@ save all housekeeping data to each output file
    for (int i=0; i<n_hk_in; i++) {
        int n_hk_events = hk_in[i]->GetEntries();
        for(long int event=0; event<n_hk_events; event++){
            hk_in[i]->GetEntry(event);
            hk_out_data_002_010[i]->Fill();
            hk_out_data_010_025[i]->Fill();
            hk_out_data_025_050[i]->Fill();
            hk_out_data_050_100[i]->Fill();
            hk_out_data_100_500[i]->Fill();
            hk_out_data_500_000[i]->Fill();
            hk_out_data_photon[i]->Fill();
            //hk_out_data_photon2[i]->Fill();
        }
    }

    //@ START of EVENT LOOP
    for(long int event=first_event; event<=last_event; event++){
        pass_photon=false;
        pass_photon2=false;
        pass_event=true;
        event_local++;
        pev = ch_in->GetDmpEvent(event);
        if (photon_filter(pev)) pass_photon=true;
        if (photon_filter2(pev)) pass_photon=true;

        if (verbosity==0) if ((event-first_event)>0 && (event-first_event)%10000==0){
                logfile = fopen("progress.log","a");
                fprintf(logfile,"%ld events processed\n", event-first_event+1);
                fclose(logfile);
                printf("%ld events processed\n", event-first_event); }

        t_in->GetEntry(event);
        if (!rm_filled) rm_in->GetEntry(event);

        /////////////////////////////////////////////////////////////////////////////////////////////

        double bgoTotalE = bgorec->GetTotalEnergy();
        std::vector<short> vecshort;
        std::vector<std::vector<short> >   layerBarIndex;  //arrange BGO bars by layer
        std::vector<std::vector<short> >   layerBarNumber;
        for(int k = 0; k <14; k++) {
            layerBarIndex   .push_back(vecshort);
            layerBarNumber  .push_back(vecshort);
        }
        int nBgoHits = bgohits->GetHittedBarNumber();
        for (int ihit = 0; ihit <nBgoHits; ihit++){
            short layerID = bgohits-> GetLayerID(ihit);
            int iBar = ((bgohits-> fGlobalBarID)[ihit]>>6) & 0x1f;
            layerBarIndex[layerID] .push_back(ihit);
            layerBarNumber[layerID].push_back(iBar);
        }
        double rmsLayer[14];
        double fracLayer[14];
        double eLayer[14];
        double eCoreLayer[14];
        double eCoreCoord[14];
        double sumRms = 0;
        for(int lay = 0; lay <14; lay++) {
            int imax = -1;
            double maxE = 0;
            for(unsigned int ind = 0; ind <layerBarNumber[lay].size(); ind++) {
                int ihit = layerBarIndex[lay][ind];
                double hitE = (bgohits->fEnergy)[ihit];
                if(hitE > maxE) {
                    maxE = hitE;
                    imax = ihit;
                }
            }
            rmsLayer [lay] = 0;
            fracLayer[lay] = 0;
            eLayer[lay]    = 0;
            if(maxE > 0) {
                int iBarMax = ((bgohits-> fGlobalBarID)[imax]>>6) & 0x1f;
                eCoreLayer[lay] = maxE;
                double coordMax = lay%2 ? bgohits->GetHitX(imax) : bgohits->GetHitY(imax);
                eCoreCoord[lay] = maxE*coordMax;
                if(iBarMax > 0 && iBarMax < 21) {
                    for(unsigned int ind = 0; ind <layerBarNumber[lay].size(); ind++) {
                        int ihit = layerBarIndex[lay][ind];
                        int iBar = ((bgohits-> fGlobalBarID)[ihit]>>6) & 0x1f;
                        if(iBar-iBarMax==1 || iBar-iBarMax==-1) {
                            double hitE = (bgohits->fEnergy)[ihit];
                            double thisCoord = lay%2 ? bgohits->GetHitX(ihit) : bgohits->GetHitY(ihit);
                            eCoreLayer[lay] += hitE;
                            eCoreCoord[lay] += hitE*thisCoord;
                        }
                    }
                }
                eCoreCoord[lay] /= eCoreLayer[lay];
                for(unsigned int ind = 0; ind <layerBarNumber[lay].size(); ind++) {
                    int ihit = layerBarIndex[lay][ind];
                    double hitE = (bgohits->fEnergy)[ihit];
                    double thisCoord = lay%2 ? bgohits->GetHitX(ihit) : bgohits->GetHitY(ihit);
                    eLayer[lay]   += hitE;
                    rmsLayer[lay] += hitE*(thisCoord-eCoreCoord[lay])*(thisCoord-eCoreCoord[lay]);
                }
                rmsLayer[lay]  = sqrt(rmsLayer[lay]/eLayer[lay]);
                fracLayer[lay] = eLayer[lay]/bgoTotalE;
                if(layerBarNumber[lay].size()<=1) {
                    rmsLayer[lay]  = 0;
                }
            }
            sumRms += rmsLayer[lay];
        }
        double Xtr=sumRms*sumRms*sumRms*sumRms*fracLayer[13]/8000000.;

        //////////////////////////////////////

        double ELayer_max_XZ = 0;
        double ELayer_max_YZ = 0;
        for (int i=1; i<14; i=i+2) { double e=bgorec->GetELayer(i); if (e > ELayer_max_XZ) {ELayer_max_XZ = e; }}
        for (int i=0; i<14; i=i+2) { double e=bgorec->GetELayer(i); if (e > ELayer_max_YZ) {ELayer_max_YZ = e; }}

        // cut maxElayer
        double MaxELayer;
        if (ELayer_max_XZ > ELayer_max_YZ) MaxELayer = ELayer_max_XZ;
        else MaxELayer = ELayer_max_YZ;
        bool passed_maxELayerTotalE_cut = true;
        double rMaxELayerTotalE = MaxELayer/bgoTotalE;
        if(rMaxELayerTotalE>0.35) passed_maxELayerTotalE_cut = false;

        // cut maxBarLayer
        bool  passed_maxBarLayer_cut = true;
        short  barNumberMaxEBarLay1_2_3[3] = {-1}; //bar number of maxE bar in layer 1, 2, 3
        double MaxEBarLay1_2_3[3] = {0};           //E of maxE bar in layer 1, 2, 3
        for (int ihit = 0; ihit <nBgoHits; ihit++){
            double hitE = (bgohits->fEnergy)[ihit];
            short   lay = bgohits->GetLayerID(ihit);
            if(lay==1 || lay==2 || lay==3) {
                if(hitE>MaxEBarLay1_2_3[lay-1]) {
                    int iBar = ((bgohits->fGlobalBarID)[ihit]>>6) & 0x1f;
                    MaxEBarLay1_2_3[lay-1] = hitE;
                    barNumberMaxEBarLay1_2_3[lay-1] = iBar; }}}
        for (int j = 0; j <3; j++){
            if(barNumberMaxEBarLay1_2_3[j] <=0 || barNumberMaxEBarLay1_2_3[j] == 21) passed_maxBarLayer_cut = false; }

        // BGO tack containment cut
        double BGO_TopZ = 46;
        double BGO_BottomZ = 448;
        double bgoRec_slope[2];
        double bgoRec_intercept[2];
        bgoRec_slope[1] = bgorec->GetSlopeXZ();
        bgoRec_slope[0] = bgorec->GetSlopeYZ();
        bgoRec_intercept[1] = bgorec->GetInterceptXZ();
        bgoRec_intercept[0] = bgorec->GetInterceptYZ();
        if( (bgoRec_slope[1]==0 && bgoRec_intercept[1]==0) ||
            (bgoRec_slope[0]==0 && bgoRec_intercept[0]==0)) pass_event=false;

        bool passed_bgo_containment_cut = false;
        TVector3 bgoRecEntrance;
        double topX = bgoRec_slope[1]*BGO_TopZ + bgoRec_intercept[1];
        double topY = bgoRec_slope[0]*BGO_TopZ + bgoRec_intercept[0];
        TVector3 bgoRecExit;
        double bottomX = bgoRec_slope[1]*BGO_BottomZ + bgoRec_intercept[1];
        double bottomY = bgoRec_slope[0]*BGO_BottomZ + bgoRec_intercept[0];
        if(fabs(topX)<280 && fabs(topY)<280 && fabs(bottomX)<280 &&  fabs(bottomY)<280) passed_bgo_containment_cut = true;

        //////////////////////////////////////

        //////// 1
        if (apply_cut>0) {
            if (!passed_bgo_containment_cut) pass_event=false;
        }
        //////// 2
        if (apply_cut>1) {
            if (!passed_maxELayerTotalE_cut) pass_event=false;
            if (!passed_maxBarLayer_cut) pass_event=false;
        }
        //////// 3
        bool passed_Xtr_cut = true;
        /* SKIP XTR
        if (apply_cut>2) {
            if (Xtr>150) passed_Xtr_cut = false;
        }
        */

        //////////////////////////////////////

        int TeV = 1000000;
        if (pass_event){
         if (passed_Xtr_cut && bgoTotalE >= 0.02*TeV && bgoTotalE < 0.10*TeV) { f_out_data_002_010_dir->cd(); t_out_data_002_010->Fill(); }
         if (bgoTotalE >= 0.10*TeV && bgoTotalE < 0.25*TeV) { f_out_data_010_025_dir->cd(); t_out_data_010_025->Fill(); }
         if (bgoTotalE >= 0.25*TeV && bgoTotalE <  0.5*TeV) { f_out_data_025_050_dir->cd(); t_out_data_025_050->Fill(); }
         if (bgoTotalE >=  0.5*TeV && bgoTotalE <  1.0*TeV) { f_out_data_050_100_dir->cd(); t_out_data_050_100->Fill(); }
         if (bgoTotalE >=  1.0*TeV && bgoTotalE <  5.0*TeV) { f_out_data_100_500_dir->cd(); t_out_data_100_500->Fill(); }
         if (bgoTotalE >=  5.0*TeV)                         { f_out_data_500_000_dir->cd(); t_out_data_500_000->Fill(); }
        }
        if (pass_photon)                                   { f_out_data_photon_dir->cd(); t_out_data_photon->Fill(); }
        //if (pass_photon2)                                  { f_out_data_photon2_dir->cd(); t_out_data_photon2->Fill(); }
        if (!rm_filled) {
            f_out_data_002_010_dir->cd(); rm_out_data_002_010->Fill();
            f_out_data_010_025_dir->cd(); rm_out_data_010_025->Fill();
            f_out_data_025_050_dir->cd(); rm_out_data_025_050->Fill();
            f_out_data_050_100_dir->cd(); rm_out_data_050_100->Fill();
            f_out_data_100_500_dir->cd(); rm_out_data_100_500->Fill();
            f_out_data_500_000_dir->cd(); rm_out_data_500_000->Fill();
            f_out_data_photon_dir->cd();  rm_out_data_photon->Fill();
            //f_out_data_photon2_dir->cd(); rm_out_data_photon2->Fill();
            rm_filled = true; }

    }//@ END OF EVENT LOOP

    f_out_data_002_010_dir->cd(); t_out_data_002_010->Write(); rm_out_data_002_010->Write(); TDirectory *hk_out_data_002_010_dir = f_out_data_002_010_dir->mkdir("HousekeepingData"); hk_out_data_002_010_dir->cd(); for (int i=0; i<n_hk_in; i++) hk_out_data_002_010[i]->Write(); f_out_data_002_010->Close();
    f_out_data_010_025_dir->cd(); t_out_data_010_025->Write(); rm_out_data_010_025->Write(); TDirectory *hk_out_data_010_025_dir = f_out_data_010_025_dir->mkdir("HousekeepingData"); hk_out_data_010_025_dir->cd(); for (int i=0; i<n_hk_in; i++) hk_out_data_010_025[i]->Write(); f_out_data_010_025->Close();
    f_out_data_025_050_dir->cd(); t_out_data_025_050->Write(); rm_out_data_025_050->Write(); TDirectory *hk_out_data_025_050_dir = f_out_data_025_050_dir->mkdir("HousekeepingData"); hk_out_data_025_050_dir->cd(); for (int i=0; i<n_hk_in; i++) hk_out_data_025_050[i]->Write(); f_out_data_025_050->Close();
    f_out_data_050_100_dir->cd(); t_out_data_050_100->Write(); rm_out_data_050_100->Write(); TDirectory *hk_out_data_050_100_dir = f_out_data_050_100_dir->mkdir("HousekeepingData"); hk_out_data_050_100_dir->cd(); for (int i=0; i<n_hk_in; i++) hk_out_data_050_100[i]->Write(); f_out_data_050_100->Close();
    f_out_data_100_500_dir->cd(); t_out_data_100_500->Write(); rm_out_data_100_500->Write(); TDirectory *hk_out_data_100_500_dir = f_out_data_100_500_dir->mkdir("HousekeepingData"); hk_out_data_100_500_dir->cd(); for (int i=0; i<n_hk_in; i++) hk_out_data_100_500[i]->Write(); f_out_data_100_500->Close();
    f_out_data_500_000_dir->cd(); t_out_data_500_000->Write(); rm_out_data_500_000->Write(); TDirectory *hk_out_data_500_000_dir = f_out_data_500_000_dir->mkdir("HousekeepingData"); hk_out_data_500_000_dir->cd(); for (int i=0; i<n_hk_in; i++) hk_out_data_500_000[i]->Write(); f_out_data_500_000->Close();
    f_out_data_photon_dir->cd(); t_out_data_photon->Write(); rm_out_data_photon->Write(); TDirectory *hk_out_data_photon_dir = f_out_data_photon_dir->mkdir("HousekeepingData"); hk_out_data_photon_dir->cd(); for (int i=0; i<n_hk_in; i++) hk_out_data_photon[i]->Write(); f_out_data_photon->Close();
    // f_out_data_photon2_dir->cd(); t_out_data_photon2->Write(); rm_out_data_photon2->Write(); TDirectory *hk_out_data_photon2_dir = f_out_data_photon2_dir->mkdir("HousekeepingData"); hk_out_data_photon2_dir->cd(); for (int i=0; i<n_hk_in; i++) hk_out_data_photon2[i]->Write(); f_out_data_photon2->Close();

    double analyzed_time = (time_finish-time_start)/60.0/60.0/24.0;
    printf("\nAnalyzed time interval: %.4f days\n",analyzed_time);
    logfile = fopen("progress.log","a");
    fprintf(logfile,"\nAnalyzed time interval: %.4f days\n",analyzed_time);
    fclose(logfile);

    printf("\nAll done!!!\n");
    return 1;
}
