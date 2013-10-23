/***************************************************************************** 
 * Project: RooFit                                                           * 
 *                                                                           * 
 * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/ 

// Your description goes here... 

#include "Riostream.h" 

#include "B2DXFitters/HistPID2D.h" 
#include "TString.h"
#include "TNamed.h"
#include <math.h> 
#include <vector>
#include <string>
#include "TH2F.h"
#include "TFile.h"
#include "TAxis.h"
#include "RooBinning.h"

HistPID2D::HistPID2D(const TString& name, const TString& title)
{
  TNamed(name,title);
  _polarity.push_back("");
  _polarity.push_back("");

  _fileName.push_back("");
  _fileName.push_back("");
  
  _hist.push_back(NULL);
  _hist.push_back(NULL);
}

HistPID2D::HistPID2D(const TString& name, const TString& title, const TString& filesDir, const TString& sig1, const TString& sig2)
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

  TH2F*_hist11= NULL;
  TH2F*_hist12= NULL;

  TString  fileName11 = FileName1[0]+FileName1[1];
  TFile* file11 = TFile::Open(fileName11.Data());
  _hist11 = (TH2F*)file11->Get(name.Data());
  
  TString  fileName12 = FileName1[0]+FileName1[2];
  TFile* file12 = TFile::Open(fileName12.Data());
  _hist12  = (TH2F*)file12->Get(name.Data());

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
  TH2F* _hist21 = NULL;
  TH2F* _hist22 = NULL;
  TString _polarity21 = "";
  TString _polarity22 = "";
  
  if (sig2 != "") 
    {
      
      fileName21 = FileName2[0]+FileName2[1];
      file21 = (TFile*)TFile::Open(fileName21.Data());
      _hist21 = (TH2F*)file21->Get(name.Data());

      fileName22 = FileName2[0]+FileName2[2];
      file22 = (TFile*)TFile::Open(fileName22.Data());
      _hist22  = (TH2F*)file22->Get(name.Data());

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
	  TH2F* histA1 = NULL;
	  TH2F* histA2 = NULL;
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
	  
	  Int_t numbinX = histA1 -> GetNbinsX();
	  TAxis* axisX=histA1->GetXaxis();
	  Double_t maxX = axisX->GetXmax();
	  Double_t minX = axisX->GetXmin();;
	  RooBinning* BinX = new RooBinning(minX,maxX,"P");
	  for (int k = 1; k < numbinX; k++ )
	    {
	      Double_t cen = histA1->ProjectionX()->GetBinCenter(k);
	      Double_t width = histA1->ProjectionX()->GetBinWidth(k);
	      maxX = cen + width/2;
	      BinX->addBoundary(maxX);
	      //std::cout<<"k: "<<k<<" max: "<<max<<" cen: "<<cen<<" =? "<<max-width/2<<" w: "<<width<<std::endl;
	    }

	  Int_t numbinY = histA1 -> GetNbinsY();
          TAxis* axisY=histA1->GetYaxis();
          Double_t maxY = axisY->GetXmax();
          Double_t minY = axisY->GetXmin();;
          RooBinning* BinY = new RooBinning(minY,maxY,"P");
          for (int k = 1; k < numbinY; k++ )
            {
              Double_t cen = histA1->ProjectionY()->GetBinCenter(k);
              Double_t width = histA1->ProjectionY()->GetBinWidth(k);
              maxY = cen + width/2;
              BinY->addBoundary(maxY);
              //std::cout<<"k: "<<k<<" max: "<<max<<" cen: "<<cen<<" =? "<<max-width/2<<" w: "<<width<<std::endl;
            }

	  histA2->SetBins(BinX->numBins(), BinX->array(), BinY->numBins(), BinY->array());
	  
	  TString namehist1 = histA1->GetName();
	  TString nameHist = namehist1+"_"+_polarity[i]+"_weighted";
	  _hist[i] = new TH2F(nameHist.Data(), histA1->GetTitle(), BinX->numBins(), BinX->array(), BinY->numBins(), BinY->array());
	  
	  for(int j=0; j<numbinX; j++)
	    {
	      for( int k = 0; j<numbinY; k++)
		{
		  Double_t bin1 = histA1->GetBinContent(j,k);
		  Double_t bin2 = histA2->GetBinContent(j,k);
		  Double_t bin = (bin1*w1+bin2*w2)/w;
		  //std::cout<<"i: "<<i<<" bin1: "<<bin1<<" bin2: "<<bin2<<" bin: "<<bin<<std::endl;
		  _hist[i]->SetBinContent(j,k,bin);
		}
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

HistPID2D::HistPID2D(const HistPID2D& other) :
  TNamed(other){

  _polarity = other._polarity;
  _fileName = other._fileName;
  _hist = other._hist;
}


ostream & operator<< (ostream &out, const HistPID2D &s)         
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


HistPID2D::~HistPID2D() { }

