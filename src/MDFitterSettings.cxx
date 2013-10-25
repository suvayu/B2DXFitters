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

#include "B2DXFitters/MDFitterSettings.h" 
#include "TString.h"
#include "RooRealVar.h"
#include "TNamed.h"
#include "TCut.h"
#include "TMath.h" 

#include <vector>
#include <fstream>



MDFitterSettings::MDFitterSettings(const TString& name, const TString& title)
{
  TNamed(name,title);

  _PIDBach = 0;
  _PIDChild = 0;
  _PIDProton = 0;

  _weightDim = 0.0;

  for (int i =  0; i < 2; i++ )
    {
      _massBRange.push_back(0.0);
      _massDRange.push_back(0.0);
      _timeRange.push_back(0.0);
      _pRange.push_back(0.0);
      _ptRange.push_back(0.0);
      _PIDRange.push_back(0.0);
      _nTracksRange.push_back(0.0);
      _BDTGRange.push_back(0.0);
      _terrRange.push_back(0.0);
      _tagRange.push_back(0.0);
      _tagOmegaRange.push_back(0.0);
      _idRange.push_back(0.0);
    }

  for (int i =  0; i < 3; i++)
    {
      _lumRatio.push_back(0.0);
      _bin.push_back(0);
      _var.push_back("");
      _calibPion.push_back("");
      _calibKaon.push_back("");
      _calibProton.push_back("");
    }

  _mVar = "";
  _mDVar = "";
  _tVar = "";
  _terrVar = "";
  _tagVar = "";
  _tagOmegaVar = "";
  _idVar = "";
  _PIDVar = "";
  _BDTGVar = "";
  _nTracksVar = "";
  _pVar = "";
  _ptVar = "";
  
  _addVar = false;
}


MDFitterSettings::MDFitterSettings(const TString& name, const TString& title, TString& nameFile)
{
  TNamed(name,title);

  Double_t vD;
  Int_t iD;
  std::string tD;
  size_t f, l, l1, l2;
  std::string tmp;
  std::string line;
  std::ifstream myfile(nameFile.Data());   
  

  _PIDBach = 0;
  _PIDChild = 0;
  _PIDProton = 0;

  _weightDim = 0.0; 

  for (int i =  0; i < 2; i++ )
    {
      _massBRange.push_back(0.0);
      _massDRange.push_back(0.0);
      _timeRange.push_back(0.0);
      _pRange.push_back(0.0);
      _ptRange.push_back(0.0);
      _PIDRange.push_back(0.0);
      _nTracksRange.push_back(0.0);
      _BDTGRange.push_back(0.0);
      _terrRange.push_back(0.0);
      _tagRange.push_back(0.0);
      _tagOmegaRange.push_back(0.0);
      _idRange.push_back(0.0);
    }

  for (int i =  0; i < 3; i++)
    {
      _lumRatio.push_back(0.0);
      _bin.push_back(0); 
      _var.push_back("");
      _calibPion.push_back("");
      _calibKaon.push_back("");
      _calibProton.push_back("");
    }

  _mVar = "";
  _mDVar = "";
  _tVar = "";
  _terrVar = "";
  _tagVar = "";
  _tagOmegaVar = "";
  _idVar = "";
  _PIDVar = "";
  _BDTGVar = "";
  _nTracksVar = "";
  _pVar = "";
  _ptVar = "";

  _addVar = false;
  
  if (myfile.is_open())
    {
      while(myfile.good())
	{
	  getline (myfile,line,'=');
	  //std::cout<<"good: "<<line<<std::endl;
	  if( line.find("BMass") != std::string::npos )     
	    {
	      getline(myfile, line, ',');
	      l1 = line.find_first_of("[");
	      line = line.substr(l1+1,line.size());
	      _massBRange[0] = (Double_t)atof(line.c_str());
	      getline(myfile, line, ']');
	      _massBRange[1] = (Double_t)atof(line.c_str());
	    }
	  if( line.find("DMass") != std::string::npos )     
	    {
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _massDRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _massDRange[1] = (Double_t)atof(line.c_str());
	    }
	  if( line.find("Time")  != std::string::npos )      
	    {  
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _timeRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _timeRange[1] = (Double_t)atof(line.c_str());
	    }
	  if( line.find("Momentum") != std::string::npos )     
	    {  
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _pRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _pRange[1] = (Double_t)atof(line.c_str());
	    }
	  if( line.find("TrMom") != std::string::npos )        
	    { 
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _ptRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _ptRange[1] = (Double_t)atof(line.c_str());
	    }
	  if( line.find("PIDK") != std::string::npos )      
	    {  
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _PIDRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _PIDRange[1] = (Double_t)atof(line.c_str());
 
	    } 
	  if( line.find("nTracks") != std::string::npos )   
	    { 
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _nTracksRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _nTracksRange[1] = (Double_t)atof(line.c_str());
	    }
	  if( line.find("BDTG") != std::string::npos )      
	    {
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _BDTGRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _BDTGRange[1] = (Double_t)atof(line.c_str());
	    }
	  if( line.find("TagDec") != std::string::npos )       
	    { 
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _tagRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _tagRange[1] = (Double_t)atof(line.c_str());
	    }
	  if( line.find("TagOmega") != std::string::npos )  
	    {  
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _tagOmegaRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _tagOmegaRange[1] = (Double_t)atof(line.c_str());
	    }
          if( line.find("Terr") != std::string::npos )      
	    { 
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _terrRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _terrRange[1] = (Double_t)atof(line.c_str());
	    }
	  if( line.find("BachCharge") != std::string::npos )        
	    {
	      getline(myfile, line, ',');
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
              _idRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
              _idRange[1] = (Double_t)atof(line.c_str());
	    }
          
	  if( line.find("Bin1") != std::string::npos )        {  myfile>>iD; _bin[0] = iD; }
          if( line.find("Bin2") != std::string::npos )        {  myfile>>iD; _bin[1] = iD; }
          if( line.find("Bin3") != std::string::npos )        {  myfile>>iD; _bin[2] = iD; }

	  if( line.find("Var1") != std::string::npos )       
	    {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _var[0] = tD.substr(f+1,l-1);   }
          if( line.find("Var2") != std::string::npos )       
	    {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _var[1] = tD.substr(f+1,l-1); }
          if( line.find("Var3") != std::string::npos )       
	    {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _var[2] = tD.substr(f+1,l-1); }

	  if( line.find("PIDBach") != std::string::npos )   {  myfile>>iD; _PIDBach = iD; }
          if( line.find("PIDChild") != std::string::npos )  {  myfile>>iD; _PIDChild = iD; }
          if( line.find("PIDProton") != std::string::npos ) {  myfile>>iD; _PIDProton = iD; }

	  if( line.find("lumRatioUp") != std::string::npos ) {  if( _lumRatio[0] == 0.0 ) { myfile>>vD; _lumRatio[0] = vD; } }
	  if( line.find("lumRatioDown") != std::string::npos ) {  if( _lumRatio[1] == 0.0 ) {myfile>>vD; _lumRatio[1] = vD;} }
	  
	  if( line.find("WeightingDimensions") != std::string::npos ) {  myfile>>iD; _weightDim = iD; }
	  
	  if( line.find("fileCalibPionUp") != std::string::npos ) 
	    {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _calibPion[0]=tD.substr(f+1,l-1); }
          if( line.find("fileCalibPionDown") != std::string::npos ) 
	    {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _calibPion[1]=tD.substr(f+1,l-1); }
          if( line.find("workCalibPion") != std::string::npos ) 
	    {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _calibPion[2]=tD.substr(f+1,l-1); }

	  if( line.find("fileCalibKaonUp") != std::string::npos )
            {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _calibKaon[0] = tD.substr(f+1,l-1); }
          if( line.find("fileCalibKaonDown") != std::string::npos )
            {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _calibKaon[1] = tD.substr(f+1,l-1); }
          if( line.find("workCalibKaon") != std::string::npos )
            {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _calibKaon[2] = tD.substr(f+1,l-1); }

	  if( line.find("fileCalibProtonUp") != std::string::npos )
            {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _calibProton[0] = tD.substr(f+1,l-1); }
          if( line.find("fileCalibProtonDown") != std::string::npos )
            {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _calibProton[1] = tD.substr(f+1,l-1); }
          if( line.find("workCalibProton") != std::string::npos )
            {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _calibProton[2] = tD.substr(f+1,l-1); }

	  if ( line.find("AdditionalVariables") != std::string::npos )
	    {
	      getline (myfile,line,']');
	      while ( line.find_first_of("\"") < line.size() && line.find_first_of("\"") != 0 )
		{
		  l1 = line.find_first_of("\"");
		  tmp = line.substr(l1+1, line.size()); 
		  l2 = tmp.find_first_of("\"");
		  tmp = line.substr(l1+1,l2);
		  _addVarNames.push_back(tmp);
		  line = line.substr(l1+l2+2,line.size());
		} 
	      if(_addVarNames.size() != 0 ) { _addVar = true; }
	    }
	  if ( _addVar == true )
	    {
	      for( unsigned int i = 0; i < _addVarNames.size(); i++ )
		{
		  if ( line.find(_addVarNames[i].Data()) != std::string::npos ) 
		    {
		      getline(myfile, line, ',');
		      l1 = line.find_first_of("[");
		      line = line.substr(l1+1,line.size());
		      _addVarRD.push_back((Double_t)atof(line.c_str()));
		      getline(myfile, line, ']');
		      _addVarRU.push_back((Double_t)atof(line.c_str()));
		    }
		}
	    }
	}
    }
  if( _lumRatio[0] != 0 || _lumRatio[0] != 1) { _lumRatio[2] = _lumRatio[2] = _lumRatio[0]/(_lumRatio[1]+_lumRatio[0]);}
  else { _lumRatio[2] = 0.0; }

}

MDFitterSettings::MDFitterSettings(const MDFitterSettings& other) :
  TNamed(other){

  _massBRange   = other._massBRange;
  _massDRange   = other._massDRange;
  _timeRange    = other._timeRange;
  _tagRange     = other._tagRange;
  _terrRange    = other._terrRange;
  _tagOmegaRange= other._tagOmegaRange;
  _pRange       = other._pRange;
  _ptRange      = other._ptRange;
  _nTracksRange = other._nTracksRange;
  _BDTGRange    = other._BDTGRange; 
  _PIDRange     = other._PIDRange;
  _idRange      = other._idRange;

  _bin = other._bin;
  _var = other._var;

  _PIDBach   = other._PIDBach;
  _PIDChild  = other._PIDChild;
  _PIDProton = other._PIDProton;

  _lumRatio = other._lumRatio;
  _weightDim = other._weightDim;
  _calibPion   = other._calibPion;
  _calibKaon   = other._calibKaon;
  _calibProton = other._calibProton;

  _mVar          = other._mVar;
  _mDVar         = other._mDVar;
  _tVar          = other._tVar;
  _terrVar       = other._terrVar;
  _tagVar        = other._tagVar;
  _tagOmegaVar   = other._tagOmegaVar;
  _idVar         = other._idVar;
  _PIDVar        = other._PIDVar;
  _BDTGVar       = other._BDTGVar;
  _nTracksVar    = other._nTracksVar;
  _pVar          = other._pVar;
  _ptVar         = other._ptVar;

  _addVarNames = other._addVarNames;
  _addVarRU = other._addVarRU;
  _addVarRD = other._addVarRD;
  _addVar  = other._addVar;


}

MDFitterSettings::~MDFitterSettings() { }

std::ostream & operator<< (std::ostream &out, const MDFitterSettings &s)
{
  out<<"MDFitterSettings("<<s.GetName()<<","<<s.GetTitle()<<")"<<std::endl;
  out<<"B(s) mass range: ("<<s._massBRange[0]<<","<<s._massBRange[1]<<"), variable name: "<<s._mVar<<std::endl;
  out<<"D(s) mass range: ("<<s._massDRange[0]<<","<<s._massDRange[1]<<"), variable name: "<<s._mDVar<<std::endl;
  out<<"PIDK range: ("<<s._PIDRange[0]<<","<<s._PIDRange[1]<<"),  variable name: "<<s._PIDVar<<std::endl;
  out<<"BDTG range: ("<<s._BDTGRange[0]<<","<<s._BDTGRange[1]<<"), variable name: "<<s._BDTGVar<<std::endl;
  out<<"Time range: ("<<s._timeRange[0]<<","<<s._timeRange[1]<<"), variable name: "<<s._tVar<<std::endl;
  out<<"Charge range: ("<<s._idRange[0]<<","<<s._idRange[1]<<"), variable name: "<<s._idVar<<std::endl;
  out<<"Tag range: ("<<s._tagRange[0]<<","<<s._tagRange[1]<<"), variable name: "<<s._tagVar<<std::endl;
  out<<"Tag omega range: ("<<s._tagOmegaRange[0]<<","<<s._tagOmegaRange[1]<<"), variable name: "<<s._tagOmegaVar<<std::endl;
  out<<"Momentum range: ("<<s._pRange[0]<<","<<s._pRange[1]<<"),  variable name: "<<s._pVar<<std::endl;
  out<<"Transverse momentum range: ("<<s._ptRange[0]<<","<<s._ptRange[1]<<"),  variable name: "<<s._ptVar<<std::endl;
  out<<"nTracks range: ("<<s._nTracksRange[0]<<","<<s._nTracksRange[1]<<"),  variable name: "<<s._nTracksVar<<std::endl;

  if( s._addVar == true )
    {
      out<<"Additional variable"<<std::endl;
      for( unsigned int i = 0; i < s._addVarNames.size(); i++ )
	{
	  out<<"Range: ("<<s._addVarRD[i]<<","<<s._addVarRU[i]<<"), variable name: "<<s._addVarNames[i]<<std::endl;
	}
    }
  
  out<<"PIDK bachelor: "<<s._PIDBach<<std::endl;
  out<<"PIDK child: "<<s._PIDChild<<std::endl;
  out<<"PIDK proton: "<<s._PIDProton<<std::endl;
  
  out<<"luminosity: magnet up: "<<s._lumRatio[0]<<" ,magnet down: "<<s._lumRatio[1]<<" ,ratio: "<<s._lumRatio[2]<<std::endl;
  out<<"weighting dimensions: "<<s._weightDim<<std::endl;
  out<<"Bin: [ "<<s._bin[0]<<" , "<<s._bin[1]<<" , "<<s._bin[2]<<" ]"<<std::endl;
  out<<"Var: [ "<<s._var[0]<<" , "<<s._var[1]<<" , "<<s._var[2]<<" ]"<<std::endl;
  
  out<<"pion calibration sample: "<<std::endl;
  out<<"\t up file: "<<s._calibPion[0]<<std::endl;
  out<<"\t down file: "<<s._calibPion[1]<<std::endl;
  out<<"\t orkspace name: "<<s._calibPion[2]<<std::endl;

  out<<"kaon calibration sample: "<<std::endl;
  out<<"\t up file: "<<s._calibKaon[0]<<std::endl;
  out<<"\t down file: "<<s._calibKaon[1]<<std::endl;
  out<<"\t workspace name: "<<s._calibKaon[2]<<std::endl;

  out<<"proton calibration sample: "<<std::endl;
  out<<"\t up file: "<<s._calibProton[0]<<std::endl;
  out<<"\t down file: "<<s._calibProton[1]<<std::endl;
  out<<"\t workspace name: "<<s._calibProton[2]<<std::endl;

  return out;
}

Double_t MDFitterSettings::GetRangeUp(TString var)
{
  Double_t range = 1234.456;
  if( var == _mVar)        { return _massBRange[1];    }
  if( var == _mDVar)       { return _massDRange[1];    }
  if( var == _tVar)        { return _timeRange[1];     } 
  if( var == _terrVar)     { return _terrRange[1];     }
  if( var == _tagVar)      { return _tagRange[1];      } 
  if( var == _tagOmegaVar) { return _tagOmegaRange[1]; }
  if( var == _idVar)       { return _idRange[1];       }
  if( var == _PIDVar)      { return _PIDRange[1];      }
  if( var == _BDTGVar)     { return _BDTGRange[1];     }
  if( var == _nTracksVar)  { return _nTracksRange[1];  }
  if( var == _pVar)        { return _pRange[1];        }
  if( var == _ptVar)       { return _ptRange[1];       }
  for ( unsigned int i = 0; i <_addVarNames.size(); i++ )
    {
      if( var == _addVarNames[i]) { return _addVarRU[i]; }
    }
  return range;
}

Double_t MDFitterSettings::GetRangeDown(TString var)
{
  Double_t range = 1234.456;
  if( var == _mVar)        { return _massBRange[0];    }
  if( var == _mDVar)       { return _massDRange[0];    }
  if( var == _tVar)        { return _timeRange[0];     }
  if( var == _terrVar)     { return _terrRange[0];     } 
  if( var == _tagVar)      { return _tagRange[0];      }
  if( var == _tagOmegaVar) { return _tagOmegaRange[0]; }
  if( var == _idVar)       { return _idRange[0];       }
  if( var == _PIDVar)      { return _PIDRange[0];      }
  if( var == _BDTGVar)     { return _BDTGRange[0];     }
  if( var == _nTracksVar)  { return _nTracksRange[0];  }
  if( var == _pVar)        { return _pRange[0];        }
  if( var == _ptVar)       { return _ptRange[0];       }
  for ( unsigned int i =0; i <_addVarNames.size(); i++ )
    {
      if( var == _addVarNames[i]) { return _addVarRD[i]; }
    }

  return range;
}

std::vector <Double_t> MDFitterSettings::GetRange(TString var)
{
  std::vector <Double_t> range;
  range.push_back(1234.456);
  range.push_back(1234.456);

  if( var == _mVar)        { return _massBRange;    }
  if( var == _mDVar)       { return _massDRange;    }
  if( var == _tVar)        { return _timeRange;     }
  if( var == _terrVar)     { return _terrRange;     }
  if( var == _tagVar)      { return _tagRange;      }
  if( var == _tagOmegaVar) { return _tagOmegaRange; }
  if( var == _idVar)       { return _idRange;       }
  if( var == _PIDVar)      { return _PIDRange;      }
  if( var == _BDTGVar)     { return _BDTGRange;     }
  if( var == _nTracksVar)  { return _nTracksRange;  }
  if( var == _pVar)        { return _pRange;        }
  if( var == _ptVar)       { return _ptRange;       }
  for (unsigned int i =0; i <_addVarNames.size(); i++ )
    {
      if( var == _addVarNames[i]) 
	{
	  range[0] = _addVarRD[i];
	  range[1] = _addVarRU[i];
	}
    }


  return range;
  
}

TCut MDFitterSettings::GetCut(TString var, bool sideband)
{
  TCut cut = "";
  TCut cut1 = "";
  TCut cut2 = "";

  Double_t range0 = GetRangeDown(var);
  Double_t range1 = GetRangeUp(var);

  if ( sideband == false )
    {
      if ( range0 != 1234.456 )
	{
	  cut1  = Form("%s > %f", var.Data(), range0); 
	}
      
      if ( range1 != 1234.456 )
	{
	  cut2  = Form("%s < %f", var.Data(), range1);
	}
      cut = cut1&&cut2;
    }
  else
    {
      if ( range0 != 1234.456 )
        {
          cut1  = Form("%s < %f", var.Data(), range0);
        }

      if ( range1 != 1234.456 )
        {
          cut2  = Form("%s > %f", var.Data(), range1);
        }
      cut = cut1||cut2;
    }
  return cut;
  
}

TCut MDFitterSettings::GetCut(bool sideband)
{
  TCut all_cut = "";

  TCut massB_cut = GetCut(_mVar, sideband);
  TCut massD_cut = GetCut(_mDVar, sideband);
  TCut time_cut = GetCut(_tVar, sideband);
  TCut terr_cut = GetCut(_terrVar, sideband);
  TCut BDTG_cut = GetCut(_BDTGVar, sideband);
  TCut nTr_cut = GetCut(_nTracksVar, sideband);
  TCut p_cut = GetCut(_pVar, sideband);
  TCut pt_cut = GetCut(_ptVar, sideband);
  TCut tag_cut = GetCut(_tagVar, sideband);
  TCut tagOmega_cut = GetCut(_tagOmegaVar, sideband);
  TCut id_cut = GetCut(_idVar, sideband);
  TCut pidk_cut = GetCut(_PIDVar, sideband);
 
  all_cut = massB_cut&&massD_cut&&time_cut&&terr_cut&&BDTG_cut&&nTr_cut&&p_cut&&pt_cut&&tag_cut&&tagOmega_cut&&id_cut&&pidk_cut; 

  return all_cut;
}

Bool_t MDFitterSettings::CheckVarName( TString name ) {
  Bool_t check = false;

  if( name == _mVar) { check = true; }
  if( name == _mDVar) { check = true;  }
  if( name == _tVar) { check = true; }
  if( name == _terrVar) { check = true; }
  if( name == _tagVar) { check = true; }
  if( name == _tagOmegaVar) { check = true; }
  if( name == _idVar) { check = true; }
  if( name == _PIDVar) { check = true; }
  if( name == _BDTGVar) { check = true; }
  if( name == _nTracksVar) { check = true; }
  if( name == _pVar) { check = true; }
  if( name == _ptVar) { check = true; }

  for(unsigned int i = 0; i<_addVarNames.size(); i++ )
    {
      if( _addVarNames[i] == name) { check = true; }
    }
  return check;
}



RooRealVar* MDFitterSettings::GetObs(TString varName, bool log)
{
  RooRealVar* Var = NULL;

  if ( CheckVarName(varName) == true )
    {
      Double_t range0 = GetRangeDown(varName);
      Double_t range1 = GetRangeUp(varName);
      
      if ( range0 != 1234.456 && range1 != 1234.456)
	{
	  if( log == false )
	    {
	      Var = new RooRealVar(varName.Data(), varName.Data(), range0, range1);
	    }
	  else
	    {
	      Var = new RooRealVar(varName.Data(), varName.Data(), TMath::Log(range0), TMath::Log(range1));
	    }
	}
    }

  return Var;
}

std::vector <TString> MDFitterSettings::GetVarNames()
{
  std::vector <TString> names;
  names.push_back(_mVar);
  names.push_back(_mDVar);
  names.push_back(_PIDVar);
  names.push_back(_tVar);
  names.push_back(_terrVar);
  names.push_back(_tagVar);
  names.push_back(_tagOmegaVar);
  names.push_back(_BDTGVar);
  names.push_back(_pVar);
  names.push_back(_ptVar);
  names.push_back(_nTracksVar);
  names.push_back(_idVar);

  for ( unsigned int i =0; i <_addVarNames.size(); i++ )
    {
      names.push_back(_addVarNames[i]);
    }

  
  return names;
}
