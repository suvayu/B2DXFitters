/*****************************************************************************                                                                                                          
 * Project: RooFit                                                           *                                                                                                          
 *                                                                           *                                                                                                          
 * Description: class contains settings for MDFitter                         *                                                                                                          
 *                                                                           *                                                                                                          
 * author: Agnieszka Dziurda  * agnieszka.dziurda@cern.ch                     *                                                                                                         
 *                                                                           *                                                                                                          
 *****************************************************************************/
// Your description goes here...                                                                                                                                                        



#include "Riostream.h"

#include "B2DXFitters/PIDCalibrationSample.h"
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/PlotSettings.h"
#include "TString.h"
#include "RooRealVar.h"
#include "RooArgSet.h"
#include "TNamed.h"
#include "TCut.h"
#include "TMath.h"

#include <vector>
#include <fstream>

using namespace GeneralUtils;

PIDCalibrationSample::PIDCalibrationSample(const TString& name, const TString& title)
{
  TNamed(name,title);

  _file = NULL;  
  _work = NULL; 
  _data = NULL; 
 
  _polarity = "unknown"; 

  _sample = "unknown";
  _year = "unknown"; 
  _stripping = "unknown";
  _fileName = "unknown";
  _workName = "RSDStCalib"; 
  _dataName = "data";
  _type = "PIDCalib"; 

  _PIDName = "unknown"; 
  _weightName = "nsig_sw";
  _var1Name = "unknown";
  _var2Name = "unknown";
 
}


PIDCalibrationSample::PIDCalibrationSample(const PIDCalibrationSample& other) :
  TNamed(other){

  _fileName = other._fileName;
  _workName = other._workName;
  _dataName = other._dataName;
  _file = other._file;
  _work= other._work;
  _data = other._data; 

  _polarity = other._polarity;
  _year = other._year;
  _stripping = other._stripping;
  _sample = other._sample;
  _type = other._type; 
  _PIDName = other._PIDName; 
  _weightName = other._weightName;
  _var1Name = other._var1Name;
  _var2Name = other._var2Name; 

}

PIDCalibrationSample::~PIDCalibrationSample() { }

std::ostream & operator<< (std::ostream &out, const PIDCalibrationSample &s)
{
  out<<"==================================================================="<<std::endl;
  out<<"PIDCalibSample for "<<s._sample<<", "<<s._year<<", "<<s._stripping<<", "<<s._polarity<<std::endl;
  out<<"-------------------------------------------------------------------"<<std::endl;
  out<<"FileName: "<<s._fileName<<std::endl;
  out<<"Type: "<<s._type<<std::endl;
  if ( s._type != "PIDCalib") 
    {
      out<<"WorkName: "<<s._workName<<std::endl;
      out<<"DataName: "<<s._dataName<<std::endl;
      out<<"PIDName: "<<s._PIDName<<std::endl;
      out<<"weightName: "<<s._weightName<<std::endl;
      out<<"var1Name: "<<s._var1Name<<std::endl;
      out<<"var2Name: "<<s._var2Name<<std::endl;
    }

  return out;
}


RooDataSet* PIDCalibrationSample::PrepareDataSet(RooRealVar* Var1, RooRealVar* Var2,
						 PlotSettings* plotSet,
						 bool debug )
{

  if ( debug == true)
    {
      std::cout << "[INFO] ==> PIDCalibrationSample::PrepareDataSet(...)."
		<< std::endl;
    }
  if ( plotSet == NULL ) { plotSet = new PlotSettings("plotSet","plotSet"); }

  RooDataSet* dataRW;

  TString nameVar1 = Var1->GetName();
  TString nameVar2 = Var2->GetName();

  if ( nameVar1 == nameVar2 ) { std::cout<<"[ERROR] The same variables: "<<nameVar1<<" == "<< nameVar2<<std::endl; return NULL;}

  RooRealVar* CalVar1 = NULL;
  CalVar1 = (RooRealVar*)_data->get()->find(_var1Name.Data());
  RooRealVar* CalVar2 = NULL;
  CalVar2 = (RooRealVar*)_data->get()->find(_var2Name.Data());
  RooRealVar* CalWeight = NULL;
  if ( _data->isWeighted() == false )
    {
      CalWeight = (RooRealVar*)_data->get()->find(_weightName.Data());
    }
  if (debug == true )
    {
      if ( CalVar1 != NULL ) { std::cout<<"[INFO] Read "<<_var1Name<<" from "<<_data->GetName()<<std::endl; } else { std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
      if ( CalVar2 != NULL ) { std::cout<<"[INFO] Read "<<_var2Name<<" from "<<_data->GetName()<<std::endl; } else{ std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
      if ( CalWeight != NULL ) { std::cout<<"[INFO] Read "<<_weightName<<" from "<<_data->GetName()<<std::endl; }
      else{
	if ( _data->isWeighted() == true ) { std::cout<<"[INFO] Weight directly taken from RooDataSet"<<std::endl; }
	else{ std::cout<<"[ERROR] Cannot read variable "<<std::endl;}
      }
    }
  
  TString namew = "weights";
  RooRealVar* weights;
  weights = new RooRealVar(namew.Data(), namew.Data(), -50.0, 50.0 );

  TString label = this->GetLabel(); 
  TString nameCalib = "CalibSample"+label; 

  dataRW = new RooDataSet(nameCalib.Data(),nameCalib.Data(),RooArgSet(*Var1,*Var2,*weights), namew.Data());

  for (Long64_t jentry=0; jentry<_data->numEntries(); jentry++)
    {
      if ( jentry == 0 ) { std::cout<<"[INFO] 0% of sample done"<<std::endl;}
      if ( jentry == _data->numEntries()/10 ) { std::cout<<"[INFO] 10% of sample done"<<std::endl;}
      if ( jentry == _data->numEntries()/5 ) { std::cout<<"[INFO] 20% of sample done"<<std::endl;}
      if ( jentry == int(_data->numEntries()*0.3) ) { std::cout<<"[INFO] 30% of sample done"<<std::endl;}
      if ( jentry == int(_data->numEntries()*0.4) ) { std::cout<<"[INFO] 40% of sample done"<<std::endl;}
      if ( jentry == int(_data->numEntries()*0.5) ) { std::cout<<"[INFO] 50% of sample done"<<std::endl;}
      if ( jentry == int(_data->numEntries()*0.6) ) { std::cout<<"[INFO] 60% of sample done"<<std::endl;}
      if ( jentry == int(_data->numEntries()*0.7) ) { std::cout<<"[INFO] 70% of sample done"<<std::endl;}
      if ( jentry == int(_data->numEntries()*0.8) ) { std::cout<<"[INFO] 80% of sample done"<<std::endl;}
      if ( jentry == int(_data->numEntries()*0.9) ) { std::cout<<"[INFO] 90% of sample done"<<std::endl;}

      const RooArgSet* setInt = _data->get(jentry);
      Var1->setVal(CalVar1->getValV(setInt));
      Var2->setVal(CalVar2->getValV(setInt));
      Double_t w = 0;

      if (  _data->isWeighted() == true ) 
	{
	  w = _data->weight();
	}
      else if ( _sample == "Combinatorial" )
	  {
	    w = 1.0; 
	  }
      else
	{
	  w = CalWeight->getValV(setInt);
	}

      weights->setVal(w); 
      dataRW->add(RooArgSet(*Var1,*Var2,*weights),w,0);
    }
  if ( dataRW != NULL  ){
    std::cout<<"[INFO] ==> Create "<<dataRW->GetName()<<std::endl;
    std::cout<<" number of entries in data set: "<<dataRW->numEntries()<<std::endl;
  } else { std::cout<<"Error in create dataset"<<std::endl; }

  dataRW->Print("v");
  TString smp = label;
  TString mode ="Calib";;
  if( plotSet->GetStatus() ==true )
    {
      SaveDataSet(dataRW, Var1 , smp, mode, plotSet, debug);
      SaveDataSet(dataRW, Var2 , smp, mode, plotSet, debug);
    }

  return dataRW;

}

void PIDCalibrationSample::ObtainVar1Name(TString check, bool debug)
{
  TString label = "";
  if ( _type == "PIDCalib" && _var1Name == "unknown" )
    {
      TString prefix = this->CheckPrefix(); 
      if ( check == "nTracks" ) {  label = "nTracks"; }
      else if ( check.Contains("PT") == true ) {  label = prefix+"_PT"; }
      else if ( check.Contains("P") == true ) {  label = prefix+"_P"; }
      else if ( check.Contains("Eta") == true ) { label = "eta"; } 

      if( debug == true) { std::cout<<"[INFO] Variable 1 name set to be: "<<label<<std::endl;}
      _var1Name = label; 
    }
}

void PIDCalibrationSample::ObtainVar2Name(TString check, bool debug)
{
  TString label = "";
  if ( _type =="PIDCalib" && _var2Name== "unknown" )
    {
      TString prefix = this->CheckPrefix();
      if ( check == "nTracks" ) {  label = "nTracks"; }
      else if ( check.Contains("PT") == true ) {  label = prefix+"_PT"; }
      else if ( check.Contains("P") == true ) {  label = prefix+"_P"; }
      else if ( check.Contains("Eta") == true ) { label= "eta"; }

      if( debug == true) { std::cout<<"[INFO] Variable 2 name set to be: "<<label<<std::endl;}
      _var2Name= label;
    }
}

void PIDCalibrationSample::ObtainPIDVarName(bool debug)
{
  TString label = "";
  if ( _type =="PIDCalib" && _PIDName== "unknown" )
    {
      label = this->CheckPIDVarName(); 
      _PIDName = label; 
      if( debug == true) { std::cout<<"[INFO] PID variable name set to be: "<<label<<std::endl;}
    }
}
