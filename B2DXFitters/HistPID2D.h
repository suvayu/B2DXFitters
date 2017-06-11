/*****************************************************************************
 * Project: RooFit                                                           *
 * Description: class contains histograms for ratio data/MC                  *
 *                                                                           * 
 * author: Agnieszka Dziurda  * agnieszka.dziurda@cern.ch                    *
 *                                                                           *
 *****************************************************************************/

#ifndef HISTPID2D
#define HISTPID2D

#include "Riostream.h"
#include "TNamed.h"
#include "TString.h"
#include "TH2F.h"
 
#include <vector>
using namespace std; 

class HistPID2D : public TNamed{

public:
  HistPID2D(){};
  HistPID2D(const TString& name, const TString& title);
  HistPID2D(const TString& name, const TString& title, const TString& fileDir, const TString& FileName1, const TString& FileName2 = "");
  
  HistPID2D(const HistPID2D& other);
  virtual TObject* clone() const { return new HistPID2D(*this); }

  friend std::ostream & operator<< (std::ostream &out, const HistPID2D &s);
  virtual ~HistPID2D();
  
  virtual void Print(Option_t * /*option*/ = "") const { std::cout<<*this<<std::endl;}

  
  TH2F* GetHist(TString& pol) { 
    if ( _polarity[0] == pol ) { return _hist[0]; } 
    else if ( _polarity[1] == pol ) { return _hist[1]; } 
    else { return NULL;}
  }
  
  TString GetFileName(TString& pol) {
    if ( _polarity[0] == pol ) { return _fileName[0]; }
    else if ( _polarity[1] == pol ) { return _fileName[1]; }
    else { return "";}
  }

  std::vector <TH2F*> GetHist() { return _hist; }
  std::vector <TString> GetFileName() { return _fileName; }
  std::vector <TString> GetPolarity() { return _polarity; }

  std::pair <Double_t,Double_t> GetValues(TString key1, TString key2, 
					  std::vector <TString> &basicName, std::vector <Double_t> &basicVal,
					  std::vector <TString> &tNW, std::vector <Double_t> &pRV);
  
  Double_t GetWeight(Double_t val1, Double_t val2, TString pol){
    Double_t _val = 0;
    TH2F* hist = GetHist(pol);
    Int_t bin = hist->FindBin(val1,val2);  
    _val = hist->GetBinContent(bin);
    return _val;
  }

  Double_t  GetValues(TString key1, TString key2,
                      std::vector <TString> &basicName, std::vector <Double_t> &basicVal,
                      std::vector <TString> &tNW, std::vector <Double_t> &pRV, TString pol);


  
  void SetHist( std::vector <TH2F*> hist ) { _hist = hist; }
  void SetHist( int i, TH2F* hist, TString pol, TString fileName ) { _hist[i] = hist; _polarity[i] = pol; _fileName[i] = fileName;  }
  void SetPolarity(std::vector <TString> pol) { _polarity = pol; }
  void SetFileName(std::vector <TString> fileName) { _fileName = fileName; }
  
  void SetPolarity(int i, TString pol) { _polarity[i] = pol; }
  void SetFileName(int i, TString fileName) { _fileName[i]  = fileName; }

  TString GetPolarity(int i ) { return _polarity[i]; } 

protected:

  std::vector <TString> _polarity;
  std::vector <TString> _fileName;
  std::vector <TH2F*> _hist;
    
private:
  ClassDef(HistPID2D, 1);
};
 
#endif
