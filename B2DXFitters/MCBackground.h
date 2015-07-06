/*****************************************************************************                                                                                                                
 * Project: RooFit                                                           *                                                                                                                
 *                                                                           *                                                                                                                
 * Description: class contains MC background properties                      *                                                                                                                
 *                                                                           *                                                                                                                
 * author: Agnieszka Dziurda  * agnieszka.dziurda@cern.ch                    *                                                                                                                
 *                                                                           *                                                                                                                
 *****************************************************************************/

#ifndef MCBACKGROUND
#define MCBACKGROUND

#include "TString.h"
#include "TNamed.h"
#include "TCut.h"
#include "RooRealVar.h"
#include "RooArgSet.h"
#include "math.h"
#include "TFile.h"
#include "TTree.h"


#include <vector>
#include <fstream>

class MCBackground : public TNamed {

public:
  MCBackground(){};
  MCBackground(const TString& name, const TString& title);
  MCBackground(const TString& name, const TString& title, TString& file, TString& sig, Int_t i);

  MCBackground(const MCBackground& other);
  virtual TObject* clone() const { return new MCBackground(*this); }

  virtual ~MCBackground();

  friend std::ostream & operator<< (std::ostream &out, const MCBackground &s);
  virtual void Print(Option_t * /*option*/ = "") const { std::cout<<*this<<std::endl;}

  TString CheckMode(); 
  TString GetMode() { return _mode; }
  TString GetFileName() { return _fileName; }
  TString GetTreeName() { return _treeName; }
  TFile* GetFile() { return _file; }
  TTree* GetTree() { return _tree; }
  Double_t GetRho() { return _rho; }
  TString GetMirror() { return _opt; }
  TString GetPolarity() { return _pol; }
  TString GetSampleMode() { TString samplemode = _mode + "_" + _pol; return samplemode; }
  TString GetYear() { return _year; }
  TString GetSampleModeYear() 
  { 
    TString smy; 
    if ( _year != "" ) { smy =  _mode + "_" + _pol+ "_" + _year; }
    else { smy = _mode + "_" + _pol; }
    return smy; 
  }

  void SetMode(TString mode ) { _mode = mode; }
  void SetFileName(TString fileName ) { _fileName = fileName; }
  void SetTreeName(TString treeName ) { _treeName = treeName; }
  void SeTree(TTree* tree ) { _tree = tree; }
  void SetFile(TFile* file ){ _file = file; }
  void SetRho(Double_t rho) { _rho = rho; }
  void SetMirror(TString mirror ) { _opt = mirror; }
  void SetPolarity(TString pol ) { _pol = pol; }
  void SetYear(TString year) { _year = year; }

  void ReloadTree(TString fileName = "", TString treeName = "")
  {
    if ( fileName != "" ) { _fileName = fileName; }
    if ( treeName != "" ) { _treeName = treeName; }
    _file = NULL;
    _tree = NULL;
    _file = TFile::Open(_fileName.Data());
    _tree = (TTree*) _file->Get(_treeName.Data());
  }

protected:

  TString _mode; 
  TString _fileName;
  TString _treeName;
  TTree* _tree;
  TFile* _file; 
  Double_t _rho;
  TString _opt; 
  TString _pol;
  TString _year; 

private:
  ClassDef(MCBackground, 1);
};

#endif
