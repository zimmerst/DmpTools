#include "Riostream.h"
#include "TDatime.h"
#include <stdio.h>
#include <time.h> 

void plot_summary(int ndays) {

  TDatime da(2015,12,26,00,00,00);
  gStyle->SetTimeOffset(da.Convert());
  gStyle->SetOptStat(0);

  ifstream in;
  in.open("raw_summary.txt");

  int year, month, day, i=1;
  long int nevt,nevt_1,nevt_2,nevt_3,nevt_4,nevt_5,nevt_6;
  long int nfiles;
  TFile *f = new TFile("plots/summary.root","RECREATE");
  TH1F *nfiles_total = new TH1F("nfiles_total","nfiles_total",ndays,0,ndays*24*60*60);
  TH1F *nevt_total = new TH1F("nevt_total","nevt_total",ndays,0,ndays*24*60*60);
  TH1F *nevt_1_total = new TH1F("nevt_002_010_total","nevt_002_010_total",ndays,0,ndays*24*60*60);
  TH1F *nevt_2_total = new TH1F("nevt_010_025_total","nevt_010_025_total",ndays,0,ndays*24*60*60);
  TH1F *nevt_3_total = new TH1F("nevt_025_050_total","nevt_025_050_total",ndays,0,ndays*24*60*60);
  TH1F *nevt_4_total = new TH1F("nevt_050_100_total","nevt_050_100_total",ndays,0,ndays*24*60*60);
  TH1F *nevt_5_total = new TH1F("nevt_100_500_total","nevt_100_500_total",ndays,0,ndays*24*60*60);
  TH1F *nevt_6_total = new TH1F("nevt_500_000_total","nevt_500_000_total",ndays,0,ndays*24*60*60);

  int daysinyears[4] = {0, // 2015 - 2015
			365, // 2016 - 2015
			365+366, // 2017 - 2015
			365+366+365}; // 2018 - 2015

  tm date = {};
  date.tm_year = 2015 - 1900;
  date.tm_mon = 11;
  date.tm_mday = 26;
  mktime( &date );
  int first_day = date.tm_yday;

  while (1) {
    in >> year >> month >> day >> nevt >> nfiles >> nevt_1 >> nevt_2 >> nevt_3 >> nevt_4 >> nevt_5 >> nevt_6;
    if (!in.good()) break;
    //printf("%10d %10d %10d %20ld %10d\n",year,month,day,nevt,nfiles);    tm date = {};
    date.tm_year = year - 1900;
    date.tm_mon = month - 1;
    date.tm_mday = day;
    mktime( &date );
    int i_day = date.tm_yday - first_day + 1 + daysinyears[year - 2015];
    //printf("%d\n",i_day);
    nevt_total->SetBinContent(i_day,nevt);
    nevt_1_total->SetBinContent(i_day,nevt_1);
    nevt_2_total->SetBinContent(i_day,nevt_2);
    nevt_3_total->SetBinContent(i_day,nevt_3);
    nevt_4_total->SetBinContent(i_day,nevt_4);
    nevt_5_total->SetBinContent(i_day,nevt_5);
    nevt_6_total->SetBinContent(i_day,nevt_6);
    nfiles_total->SetBinContent(i_day,nfiles);
    i++;
  }
  printf("DONE!\n");

  in.close();

  TCanvas *canv1 = new TCanvas("canv1","canv1",800,600);
  canv1->cd();
  //nevt_total->GetXaxis()->SetLabelSize(0.06);
  nevt_total->GetXaxis()->SetTimeDisplay(1);
  nevt_total->GetXaxis()->SetTimeFormat("%d\/%m\/%y");
  nevt_total->GetXaxis()->SetNdivisions(204,false);
  nevt_total->GetXaxis()->SetTitle("Date");
  nevt_total->GetYaxis()->SetTitle("Number of events per day");
  nevt_total->SetLineColor(kBlack);
  nevt_total->SetLineWidth(3);
  nevt_total->GetYaxis()->SetRangeUser(1,20000000);
  nevt_total->Draw();
  nevt_1_total->SetLineColor(kBlack);   nevt_1_total->Draw("SAME");
  nevt_2_total->SetLineColor(kGreen+2); nevt_2_total->Draw("SAME");
  nevt_3_total->SetLineColor(kOrange);  nevt_3_total->Draw("SAME");
  nevt_4_total->SetLineColor(kBlue);    nevt_4_total->Draw("SAME");
  nevt_5_total->SetLineColor(kGreen);   nevt_5_total->Draw("SAME");
  nevt_6_total->SetLineColor(kRed);     nevt_6_total->Draw("SAME");
  canv1->SetLogy();

  TCanvas *canv2 = new TCanvas("canv2","canv2",800,600);
  canv2->cd();
  //nfiles_total->GetXaxis()->SetLabelSize(0.06);
  nfiles_total->GetXaxis()->SetTimeDisplay(1);
  nfiles_total->GetXaxis()->SetTimeFormat("%d\/%m\/%y");
  nfiles_total->GetXaxis()->SetNdivisions(204,false);
  nfiles_total->GetXaxis()->SetTitle("Date");
  nfiles_total->GetYaxis()->SetTitle("Number of files per day");
  nfiles_total->Draw();

  TLegend *leg = new TLegend(0.1,0.6,0.48,0.8);
  leg->SetHeader("Number of events in energy bins per day");
  leg->AddEntry(nevt_total,"All","l");
  leg->AddEntry(nevt_1_total,"20 - 100 GeV","l");
  leg->AddEntry(nevt_2_total,"100 - 250 GeV","l");
  leg->AddEntry(nevt_3_total,"250 - 500 GeV","l");
  leg->AddEntry(nevt_4_total,"500 - 1000 GeV","l");
  leg->AddEntry(nevt_5_total,"1 - 5 TeV","l");
  leg->AddEntry(nevt_6_total,"> 5 TeV","l");
  canv1->cd();
  leg->Draw();

  canv1->SaveAs("plots/nevt.png");
  canv2->SaveAs("plots/nfiles.png");

  canv1->SaveAs("plots/nevt.C");
  canv2->SaveAs("plots/nfiles.C");

  f->Write();
}