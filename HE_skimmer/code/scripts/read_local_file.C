void read_local_file(TString filename){
  //  gSystem->Load("libDmpEvent.so");
  /* superseded 
  if (filename.Contains("dpm"))
    TFile *file = TFile::Open("grid05.unige.ch:1094"+filename);
  else
    TFile *file = TFile::Open(filename);
  */
  TFile *file = TFile::Open(filename);
  TTree *tree = (TTree*)file->Get("CollectionTree");
  Double_t nentries = tree->GetEntries();
  printf("nentries = %d\n",nentries);
}
