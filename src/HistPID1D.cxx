/***************************************************************************** 
 * Project: RooFit                                                           * 
 *                                                                           * 
 * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/ 

// Your description goes here... 

#include "Riostream.h" 

#include "B2DXFitters/HistPID1D.h" 
#include "TString.h"
#include "TNamed.h"
#include <math.h> 
#include <vector>
#include <string>
#include "TH1F.h"
#include "TFile.h"
#include "TAxis.h"
#include "TCanvas.h"
#include "RooBinning.h"
#include "TGraphErrors.h"
#include "TLegend.h"
#include "TLatex.h"
#include "B2DXFitters/PlotSettings.h"


HistPID1D::HistPID1D(const TString& name, const TString& title)
{
  TNamed(name,title);
  _polarity.push_back("");
  _polarity.push_back("");

  _fileName.push_back("");
  _fileName.push_back("");
  
  _hist.push_back(NULL);
  _hist.push_back(NULL);
}

HistPID1D::HistPID1D(const TString& name, const TString& title, const TString& filesDir, const TString& sig1, const TString& sig2)
{
  TNamed(name,title);

  _polarity.push_back("");
  _polarity.push_back("");

  _fileName.push_back("");
  _fileName.push_back("");

  _hist.push_back(NULL);
  _hist.push_back(NULL);
  
  std::vector <std::string> FileName1;
  std::vector <std::string> FileName2;

  std::string line;
  std::ifstream myfile(filesDir.Data());
  
  if (myfile.is_open())
    {
      while(myfile.good())
	{
	  getline (myfile,line);

	  if(line == sig1.Data() ){
	    while( line != "###" ){
	      getline (myfile,line);
	      if( line != "###"){ FileName1.push_back(line.c_str());}
	    }
	  }
	  
	  if(line == sig2.Data() && sig2 != ""){
            while( line != "###" ){
              getline (myfile,line);
              if( line != "###"){ FileName2.push_back(line.c_str());}
            }
          }

	}
    }
  else { std::cout<<"Unable to open a file"<<std::endl;}

  TH1F*_hist11= NULL;
  TH1F*_hist12= NULL;

  TString  fileName11 = FileName1[0]+FileName1[1];
  TFile* file11 = TFile::Open(fileName11.Data());
  _hist11 = (TH1F*)file11->Get(name.Data());
  
  TString  fileName12 = FileName1[0]+FileName1[2];
  TFile* file12 = TFile::Open(fileName12.Data());
  _hist12  = (TH1F*)file12->Get(name.Data());

  TString _polarity11 = "";
  TString _polarity12 = "";

  if (FileName1[1].find("MD") != std::string::npos  || 
      FileName1[1].find("down") != std::string::npos || 
      FileName1[1].find("dw") != std::string::npos ||	
      FileName1[1].find("Down") != std::string::npos || 
      FileName1[1].find("md") != std::string::npos)
    {
      _polarity11 = "down";
    }
  else if ( FileName1[1].find("MU") != std::string::npos || 
	    FileName1[1].find("up") != std::string::npos || 
	    FileName1[1].find("Up") != std::string::npos || 
	    FileName1[1].find("mu") != std::string::npos )
    {
      _polarity11 = "up";
    }
  else
    {
      _polarity11 = "both";
    }
  

  if (FileName1[2].find("MD") != std::string::npos  ||
      FileName1[2].find("down") != std::string::npos ||
      FileName1[2].find("dw") != std::string::npos ||
      FileName1[2].find("Down") != std::string::npos ||
      FileName1[2].find("md") != std::string::npos)
    {
      _polarity12 = "down";
    }
  else if ( FileName1[2].find("MU") != std::string::npos ||
            FileName1[2].find("up") != std::string::npos ||
            FileName1[2].find("Up") != std::string::npos ||
            FileName1[2].find("mu") != std::string::npos )
    {
      _polarity12 = "up";
    }
  else
    {
      _polarity12 = "both";
    }



  TString fileName21, fileName22;
  TFile* file21 = NULL;
  TFile* file22 = NULL;
  TH1F* _hist21 = NULL;
  TH1F* _hist22 = NULL;
  TString _polarity21 = "";
  TString _polarity22 = "";
  
  if (sig2 != "") 
    {
      
      fileName21 = FileName2[0]+FileName2[1];
      file21 = (TFile*)TFile::Open(fileName21.Data());
      _hist21 = (TH1F*)file21->Get(name.Data());

      fileName22 = FileName2[0]+FileName2[2];
      file22 = (TFile*)TFile::Open(fileName22.Data());
      _hist22  = (TH1F*)file22->Get(name.Data());

      
      if (FileName2[1].find("MD") != std::string::npos  ||
	  FileName2[1].find("down") != std::string::npos ||
	  FileName2[1].find("dw") != std::string::npos ||
	  FileName2[1].find("Down") != std::string::npos ||
	  FileName2[1].find("md") != std::string::npos)
	{
	  _polarity21 = "down";
	}
      else if ( FileName2[1].find("MU") != std::string::npos ||
		FileName2[1].find("up") != std::string::npos ||
		FileName2[1].find("Up") != std::string::npos ||
		FileName2[1].find("mu") != std::string::npos )
	{
	  _polarity21 = "up";
	}
      else
	{
	  _polarity21 = "both";
	}

      if (FileName2[2].find("MD") != std::string::npos  ||
	  FileName2[2].find("down") != std::string::npos ||
	  FileName2[2].find("dw") != std::string::npos ||
	  FileName2[2].find("Down") != std::string::npos ||
	  FileName2[2].find("md") != std::string::npos)
	{
	  _polarity22 = "down";
	}
      else if ( FileName1[2].find("MU") != std::string::npos ||
		FileName1[2].find("up") != std::string::npos ||
		FileName1[2].find("Up") != std::string::npos ||
		FileName1[2].find("mu") != std::string::npos )
	{
	  _polarity22 = "up";
	}
      else
	{
	  _polarity22 = "both";
	}

    }
   
  if (sig2 != "")
    {
      for ( int i = 0; i<2; i++ )
	{
	  TH1F* histA1 = NULL;
	  TH1F* histA2 = NULL;
	  TString fN1 = "";
	  TString fN2 = "";
	  if( i == 0 )
	    {
	      histA1 = _hist11;
	      fN1 = fileName11; 
	      if(_polarity11 == _polarity21 ) { histA2 = _hist21; fN2 = fileName21; }
	      else if(_polarity11 == _polarity22 ) { histA2 = _hist22; fN2 = fileName22;  }
	      else { break;}
	      _polarity[i] = _polarity11;
	    }
	  else if ( i == 1)
	    {
	      histA1 = _hist12;
	      fN1 = fileName12; 
              if(_polarity12 == _polarity21 ) { histA2 = _hist21; fN2 = fileName21; }
	      else if(_polarity12 == _polarity22) { histA2 = _hist22; fN2 = fileName22; }
	      else { break;}
	      _polarity[i] = _polarity12; 
	    }
	  Double_t w1 = histA1->GetEntries();
	  Double_t w2 = histA2->GetEntries();
	  Double_t w = w1+w2;
	  std::cout<<"[INFO] weight: "<<w1<<" + "<<w2<<" which means: "<<w1/w<<" + "<<w2/w<<std::endl; 
	  
	  Int_t numbin = histA1 -> GetNbinsX();
	  TAxis* axis=histA1->GetXaxis();
	  Double_t max = axis->GetXmax();
	  Double_t min = axis->GetXmin();;
	  std::cout<<"min: "<<min<<" max: "<<max<<std::endl;
	  RooBinning* Bin = new RooBinning(min,max,"P");
	  for (int k = 1; k < numbin; k++ )
	    {
	      Double_t cen = histA1 -> GetBinCenter(k);
	      Double_t width = histA1 -> GetBinWidth(k);
	      max = cen + width/2;
	      Bin->addBoundary(max);
	      //std::cout<<"k: "<<k<<" max: "<<max<<" cen: "<<cen<<" =? "<<max-width/2<<" w: "<<width<<std::endl;
	    }
	  histA2->SetBins(Bin->numBins(), Bin->array());
	  
	  TString namehist1 = histA1->GetName();
	  TString nameHist = namehist1+"_"+_polarity[i]+"_weighted";
	  _hist[i] = new TH1F(nameHist.Data(), histA1->GetTitle(), Bin->numBins(), Bin->array());
	  _hist[i]->SetTitle(histA1->GetTitle());
	  _hist[i]->GetXaxis()->SetTitle(histA1->GetXaxis()->GetTitle());
	  _hist[i]->GetYaxis()->SetTitle(histA1->GetYaxis()->GetTitle());

	  for(int j=0; j<numbin; j++)
	    {
	      Double_t bin1 = histA1->GetBinContent(j);
	      Double_t bin2 = histA2->GetBinContent(j);
	      Double_t bin = (bin1*w1+bin2*w2)/w;
	      //std::cout<<"i: "<<i<<" bin1: "<<bin1<<" bin2: "<<bin2<<" bin: "<<bin<<std::endl;
	      _hist[i]->SetBinContent(j,bin);

	      Double_t err1 = histA1->GetBinError(j);
	      Double_t err2 = histA2->GetBinError(j);
	      Double_t err = sqrt( w1/w*err1*err1+w2/w*err2*err2);
	      _hist[i]->SetBinError(j,err);
	      //std::cout<<"i: "<<j<<" err: "<<err1<<" err2: "<<err2<<" err: "<<err<<std::endl;
	    }
	  _fileName[i]= fN1+" weighted with "+fN2;
	}
    }
  else
    {
      _hist[0] = _hist11;
      _hist[1] = _hist12;
      _polarity[0] = _polarity11;
      _polarity[1] = _polarity12;
      TString namehist1 = _hist11->GetName();
      TString nameHist = namehist1+"_"+_polarity[0];
      _hist[0]->SetName(nameHist.Data());
      namehist1 = _hist12->GetName();
      nameHist = namehist1+"_"+_polarity[1];
      _hist[1]->SetName(nameHist.Data());
      _fileName[0]= fileName11;
      _fileName[1]= fileName12;

    }

  
  
}

HistPID1D::HistPID1D(const HistPID1D& other) :
  TNamed(other){

  _polarity = other._polarity;
  _fileName = other._fileName;
  _hist = other._hist;
}


std::ostream & operator<< (std::ostream &out, const HistPID1D &s)         
{
  out<<"HistPID("<<s.GetName()<<","<<s.GetTitle()<<")"<<std::endl;
  if ( s._hist[0] != NULL )
    {
      out<<"First histogram: "<<std::endl;
      out<<"\t Hist name: "<<s._hist[0]->GetName()<<std::endl;
      out<<"\t File Name: "<<s._fileName[0]<<std::endl;
      out<<"\t Polarity: "<<s._polarity[0]<<std::endl;
    }
  if ( s._hist[1] != NULL )
    {
      out<<"Second histogram: "<<std::endl;
      out<<"\t Histname: "<<s._hist[1]->GetName()<<std::endl;
      out<<"\t File Name: "<<s._fileName[1]<<std::endl;
      out<<"\t Polarity: "<<s._polarity[1]<<std::endl;
    }  
  return out;
}

void HistPID1D::ShowContent(TString& pol)
{
  TH1F* hist = NULL;

  if ( _polarity[0] == pol ) { hist = _hist[0]; }
  else if ( _polarity[1] == pol ) { hist =  _hist[1]; }
  Int_t numbin = hist -> GetNbinsX();
  for(int i = 0; i<numbin; i++)
    {
      Double_t bin1 = hist->GetBinContent(i);
      Double_t err1 = hist->GetBinError(i);
      std::cout<<"bin: "<<i<<" content: "<<bin1<<" with error: "<<err1<<std::endl;
    }
  
}


void HistPID1D::SavePlot(PlotSettings* plotSet)
{
  TH1F* histMD = NULL;
  TH1F* histMU = NULL;

  if ( _polarity[0] == "down" ) { histMD = _hist[0]; }
  else if ( _polarity[1] == "down" ) { histMD =  _hist[1]; }
  
  if ( _polarity[0] == "up" ) { histMU = _hist[0]; }
  else if ( _polarity[1] == "up" ) { histMU =  _hist[1]; }

  if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }
  /*
  Int_t numbinMD = histMD -> GetNbinsX();
  for(int i = 0; i<numbinMD; i++)
    {
      Double_t bin1 = histMD->GetBinContent(i);
      Double_t err1 = histMD->GetBinError(i);
      std::cout<<"bin: "<<i<<" content: "<<bin1<<" with error: "<<err1<<std::endl;
    }
  Int_t numbinMU = histMU -> GetNbinsX();
  for(int i = 0; i<numbinMU; i++)
    {
      Double_t bin1 = histMU->GetBinContent(i);
      Double_t err1 = histMD->GetBinError(i);
      std::cout<<"bin: "<<i<<" content: "<< bin1<<" with error: "<<err1<<std::endl;
    }
  */
  
  TString nameHist = histMD->GetName();
  TString remove = "";
  
  if( nameHist.Contains("weighted") == true ) { remove = "_down_weighted"; }
  else { remove = "_down"; }

  nameHist.ReplaceAll(remove, ""); 
  TString dir = plotSet->GetDir();
  TString ext = plotSet->GetExt();
  TString save = dir+"/"+nameHist+"."+ext;

  TCanvas *rat = new TCanvas("can","",10,10,800,600);
  
  histMD->SetMarkerStyle(20);
  histMU->SetMarkerStyle(26);
  //histMD->SetMarkerSize(1.2);
  //histMU->SetMarkerSize(1.2);
  histMD->SetMarkerColor(kOrange);
  histMU->SetMarkerColor(kRed);

  histMD->SetLabelFont(132,"X");
  histMD->SetLabelFont(132,"Y");
  histMU->SetLabelFont(132,"X");
  histMU->SetLabelFont(132,"Y");

  TString title = histMD->GetTitle();
  histMD->SetTitle("");
  histMU->SetTitle("");

  histMD->GetXaxis()->SetTitle("Track Momentum [MeV/c]");
  histMU->GetXaxis()->SetTitle("Track Momentum [MeV/c]");

  histMD->SetStats(false);
  histMU->SetStats(false);

  TString YTitle;

  if ( title != "")
    {
      if( nameHist.Contains("Eff") == true)
	{
	  YTitle = "Efficiency for "+title;
	}
      else
	{
	  YTitle = "MisID for "+title;
	}
      histMD->GetYaxis()->SetTitle(YTitle.Data());
      histMU->GetYaxis()->SetTitle(YTitle.Data());
    }

  TLegend* legend = NULL;
  if ( nameHist.Contains("Eff") == true )
    {
      legend = new TLegend( 0.68, 0.76, 0.88, 0.88 );
    }
  else
    {
      legend = new TLegend( 0.68, 0.12, 0.88, 0.24 );
    }
  legend->SetTextSize(0.04);
  legend->SetTextFont(12);
  legend->SetFillColor(4000);
  legend->SetShadowColor(0);
  legend->SetBorderSize(0);
  legend->SetTextFont(132);

  TGraphErrors* grMD = new TGraphErrors(5);
  grMD->SetName("grMD");
  grMD->SetLineColor(kBlack);
  grMD->SetLineWidth(1);
  grMD->SetMarkerStyle(20);
  grMD->SetMarkerSize(1.5);
  grMD->SetMarkerColor(kOrange);
  grMD->Draw("P");

  TGraphErrors* grMU = new TGraphErrors(5);
  grMU->SetName("grMU");
  grMU->SetLineColor(kBlack);
  grMU->SetLineWidth(1);
  grMU->SetMarkerStyle(26);
  grMU->SetMarkerSize(1.5);
  grMU->SetMarkerColor(kRed);
  grMU->Draw("P");

  legend->AddEntry("grMD","magnet down","lep");
  legend->AddEntry("grMU","magnet up","lep");

  TLatex* lhcbtext = new TLatex();
  lhcbtext->SetTextFont(132);
  lhcbtext->SetTextColor(1);
  lhcbtext->SetTextSize(0.05);
  lhcbtext->SetTextAlign(12);

  histMD->Draw("E1");
  histMU->Draw("same E1");
  legend->Draw("same");
  if ( nameHist.Contains("Eff") == true )
    {
      lhcbtext->DrawTextNDC( 0.78, 0.72, "LHCb");
    }
  else
    {
      lhcbtext->DrawTextNDC( 0.78 , 0.27, "LHCb");
    }
  /*
  TString nameMD = "histMD_"+nameHist+".root";
  TString nameMU = "histMU_"+nameHist+".root";
  histMD->SaveAs(nameMD.Data());
  histMU->SaveAs(nameMU.Data());
  */
  rat->Update();
  rat->SaveAs(save.Data());
 
}

HistPID1D::~HistPID1D() { }


