/*****************************************************************************
 * Project: RooFit                                                           *
 * Description: class contains histograms for PID calibration                *
 *                                                                           * 
 * author: Agnieszka Dziurda  * agnieszka.dziurda@cern.ch                    *
 *                                                                           *
 *****************************************************************************/

#ifndef HISTPID1D
#define HISTPID1D

#include "Riostream.h"
#include "TNamed.h"
#include "TString.h"
#include "TH1F.h"
#include "PlotSettings.h"
 
#include <vector>

class HistPID1D : public TNamed{

public:
  HistPID1D(){};
  HistPID1D(const TString& name, const TString& title);
  HistPID1D(const TString& name, const TString& title, const TString& fileDir, const TString& FileName1, const TString& FileName2 = "");
  
  HistPID1D(const HistPID1D& other);
  virtual TObject* clone() const { return new HistPID1D(*this); }

  friend std::ostream & operator<< (std::ostream &out, const HistPID1D &s);
  virtual ~HistPID1D();
  
  virtual void Print(Option_t * /*option*/ = "") const { std::cout<<*this<<std::endl;}

  
  TH1F* GetHist(TString& pol) { 
    if ( _polarity[0] == pol ) { return _hist[0]; } 
    else if ( _polarity[1] == pol ) { return _hist[1]; } 
    else { return NULL;}
  }
  
  TString GetFileName(TString& pol) {
    if ( _polarity[0] == pol ) { return _fileName[0]; }
    else if ( _polarity[1] == pol ) { return _fileName[1]; }
    else { return "";}
  }

  std::vector <TH1F*> GetHist() { return _hist; }
  std::vector <TString> GetFileName() { return _fileName; }
  std::vector <TString> GetPolarity() { return _polarity; }
  
  Double_t GetWeight(Double_t val, TString pol){
    Double_t _val = 0;
    TH1F* hist = GetHist(pol);
    Int_t bin = hist->FindBin(val);  
    _val = hist->GetBinContent(bin);
    return _val;
  }
  
  void SetHist( std::vector <TH1F*> hist ) { _hist = hist; }
  void SetHist( int i, TH1F* hist, TString pol, TString fileName ) { _hist[i] = hist; _polarity[i] = pol; _fileName[i] = fileName;  }
  void SetPolarity(std::vector <TString> pol) { _polarity = pol; }
  void SetFileName(std::vector <TString> fileName) { _fileName = fileName; }
  void SavePlot(PlotSettings* plotSet = NULL);
  void ShowContent(TString& pol);

  TString GetPolarity(int i ) { return _polarity[i]; }

protected:

  std::vector <TString> _polarity;
  std::vector <TString> _fileName;
  std::vector <TH1F*> _hist;
    
private:
  ClassDef(HistPID1D, 1);
};
 
#endif
