/*****************************************************************************                                                                                                          
 * Project: RooFit                                                           *                                                                                                          
 *                                                                           *                                                                                                          
 * Description: class contains settings for MDFitter                         *                                                                                                          
 *                                                                           *                                                                                                          
 * author: Agnieszka Dziurda  * agnieszka.dziurda@cern.ch                    *                                                                                                           *                                                                           *                                                                                                          
 *****************************************************************************/

#ifndef PIDCALIBRATIONSAMPLE
#define PIDCALIBRATIONSAMPLE

#include "TString.h"
#include "TNamed.h"
#include "TCut.h"
#include "RooRealVar.h"
#include "RooArgSet.h"
#include "TFile.h"
#include "RooWorkspace.h" 
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/PlotSettings.h"


#include "math.h"

#include <vector>
#include <fstream>

using namespace GeneralUtils;


class PIDCalibrationSample : public TNamed {

 public:
  PIDCalibrationSample(){};
  PIDCalibrationSample(const TString& name, const TString& title);

  PIDCalibrationSample(const PIDCalibrationSample& other);
  virtual TObject* clone() const { return new PIDCalibrationSample(*this); }

  virtual ~PIDCalibrationSample();

  friend std::ostream & operator<< (std::ostream &out, const PIDCalibrationSample &s);
  virtual void Print(Option_t * /*option*/ = "") const { std::cout<<*this<<std::endl;}

  void SetFile(TString  file, bool debug = false) 
  { 
    TFile* filetmp = TFile::Open(file.Data());
    if ( debug == true ) { std::cout<<"[INFO] File: "<<file<<" opened sucessfully."<<std::endl; }
    _file = filetmp; 
    _fileName = file;
    TString label = this->GetLabel();  
    if (debug == true ) { std::cout<<"[INFO] File set to: "<<label<<std::endl;   }
  }
 
  void LoadWorkspace(TString workName, bool debug = false)
  {
    _work = (RooWorkspace*)_file->Get(workName.Data()); 
    _workName = workName; 
     
    if ( _work == NULL ) { std::cout<<"[ERROR] Workspace: "<<_workName<<" does not exist in this file. "<<std::endl; _file->ls(); }
    {
      if ( debug == true ) 
	{ 
	  std::cout<<"[INFO] Workspace "<<_workName<<" opened sucessfully."<<std::endl; 
	}
    }
    
  }
  
  void LoadWorkspace(bool debug = false)
  {
    _work = (RooWorkspace*)_file->Get(_workName.Data());

    if ( _work == NULL ) { std::cout<<"[ERROR] Workspace: "<<_workName<<" does not exist in this file. "<<std::endl; _file->ls(); }
    {
      if ( debug == true )
        {
	  std::cout<<"[INFO] Workspace "<<_workName<<" opened sucessfully."<<std::endl;
        }
    }

  }

  void LoadData(TString dataName, bool debug = false )
  {
    _data = (RooDataSet*)_work->data(dataName.Data()); 
    _dataName = dataName;
    if ( _data == NULL ) { std::cout<<"[ERROR] Data sample: "<<_dataName<<" does not exist in this workspace."<<std::endl; _work->Print(); }
    else
      {
	if (debug == true )
	  {
	    std::cout<<"[INFO] Data "<<_dataName<<" loaded sucessfully."<<std::endl;
	  }
      }
  }

  void LoadData(bool debug = false )
  {
    _data = (RooDataSet*)_work->data(_dataName.Data());
    if ( _data == NULL ) { std::cout<<"[ERROR] Data sample: "<<_dataName<<" does not exist in this workspace."<<std::endl; _work->Print(); }
    else
      {
        if (debug == true )
          {
	    std::cout<<"[INFO] Data "<<_dataName<<" loaded sucessfully."<<std::endl;
          }
      }
  }

  void SetWorkName(TString name) { _workName = name; }
  void SetPolarity(TString pol) { _polarity = pol; } 
  void SetStripping(TString strip) { _stripping = strip;}
  void SetSampleType(TString sample) { _sample = sample; }
  void SetYear(TString year) { _year = year; }
  void SetDataName(TString dataName) { _dataName = dataName; } 
  void SetType(TString type) { _type = type; }
  void SetPIDName(TString name) { _PIDName = name; }
  void SetVar1Name(TString name) { _var1Name = name; }
  void SetVar2Name(TString name) { _var2Name = name; }
  void SetWeightName(TString name) { _weightName = name; }

  TString GetStripping() { return _stripping; }
  TString GetSampleType() { return _sample; }
  TString GetYear() { return _year; }
  TFile* GetFile(){ return _file; }
  RooWorkspace* GetWorkspace() { return _work; }
  RooDataSet* GetData() { return _data; }
  

  TString GetFileName() {   return _fileName; }
  TString GetWorkName() {   return _workName; } 
  TString GetDataName() {   return _dataName; } 
  TString GetPolarity() { return _polarity; } 
  TString GetType() { return _type; } 
  TString GetLabel()
  {
    TString label = _sample + "_" + _stripping + "_" + _year + "_" + _polarity;
    return label;
  }

  TString CheckPrefix()
  {
    TString prefix = "";
    if ( _sample == "Kaon" ) { prefix = "K";} 
    else if ( _sample == "Pion") { prefix = "Pi"; }
    else if ( _sample == "Proton" ) { prefix = "P"; }
    else if ( _sample == "Combinatorial") { prefix = "Combo";}
    return prefix;
  }
  
  TString GetVar1Name(){ return _var1Name; }
  TString GetVar2Name(){ return _var2Name; }  
  TString GetWeightName(){ return _weightName; } 
  TString GetPIDName(){ return _PIDName; }  
  void ObtainVar1Name(TString check, bool debug); 
  void ObtainVar2Name(TString check, bool debug); 
  void ObtainPIDVarName(bool debug); 
  
  RooDataSet* PrepareDataSet(RooRealVar* Var1, RooRealVar* Var2, PlotSettings* plotSet, bool debug );
  
  TString CheckPIDVarName()
  {
    TString PIDName = "";
    if ( _type == "PIDCalib" )
      {
	TString TL = this->CheckPrefix();
	PIDName = TL + "_CombDLLK";
      }
    else
      {
	PIDName = _PIDName; 
      }
    return PIDName; 
  }
  

protected:
  
  TFile*  _file;
  RooWorkspace* _work;
  RooDataSet* _data; 
  TString _polarity;
  TString _stripping;
  TString _sample;
  TString _year;
  TString _fileName;
  TString _workName;
  TString _dataName; 
  TString _type; 
  TString _PIDName; 
  TString _weightName;
  TString _var1Name;
  TString _var2Name; 

 private:
  ClassDef(PIDCalibrationSample, 1);
};

#endif

