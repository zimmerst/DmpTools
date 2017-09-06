void read_local_file(TString filename){
  gSystem->Load("libDmpEvent.so");
  TFile *file = TFile::Open(filename);
  TTree *tree = (TTree*)file->Get("CollectionTree");
  Double_t nentries = tree->GetEntries();
  printf("nentries = %d\n",nentries);
}
