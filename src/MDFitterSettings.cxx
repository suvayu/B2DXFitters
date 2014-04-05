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
  _idVar = "";
  _PIDVar = "";
  _BDTGVar = "";
  _nTracksVar = "";
  _pVar = "";
  _ptVar = "";
  
  _addVar = false;
  _tagVar = false;
  _tagOmegaVar = false;

  _labX = 1;
  _addDataCuts = ""; 
  _addMCCuts = "";

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
  _idVar = "";
  _PIDVar = "";
  _BDTGVar = "";
  _nTracksVar = "";
  _pVar = "";
  _ptVar = "";

  _addVar = false;
  _tagVar = false;
  _tagOmegaVar = false;

  _labX = 1;
  _addDataCuts = "";
  _addMCCuts = "";

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
	      //std::cout<<line<<std::endl;
	      getline(myfile, line, ',');
	      //std::cout<<line<<std::endl;
              l1 = line.find_first_of("[");
              line = line.substr(l1+1,line.size());
	      //std::cout<<line<<std::endl;
	      _PIDRange[0] = (Double_t)atof(line.c_str());
              getline(myfile, line, ']');
	      //std::cout<<line<<std::endl;
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
	  if( line.find("labX") != std::string::npos )        {  myfile>>iD; _labX = iD; }

	  if( line.find("Var1") != std::string::npos )       
	    {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _var[0] = tD.substr(f+1,l-1);   }
          if( line.find("Var2") != std::string::npos )       
	    {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _var[1] = tD.substr(f+1,l-1); }
          if( line.find("Var3") != std::string::npos )       
	    {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _var[2] = tD.substr(f+1,l-1); }
	  if( line.find("AdditionalDataCuts") != std::string::npos )
            {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _addDataCuts = tD.substr(f+1,l-1);   }
	  if( line.find("AdditionalMCCuts") != std::string::npos )
            {  myfile>>tD; l=tD.find_last_of("\""); f=tD.find_first_of("\""); _addMCCuts = tD.substr(f+1,l-1);   }

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
	  
	  if ( line.find("TagDec") != std::string::npos )
            {
              getline (myfile,line,']');
              while ( line.find_first_of("\"") < line.size() && line.find_first_of("\"") != 0 )
                {
                  l1 = line.find_first_of("\"");
                  tmp = line.substr(l1+1, line.size());
                  l2 = tmp.find_first_of("\"");
                  tmp = line.substr(l1+1,l2);
                  _tagVarNames.push_back(tmp);
                  line = line.substr(l1+l2+2,line.size());
                }
              if(_tagVarNames.size() != 0 ) { _tagVar = true; }
            }
          if ( _tagVar == true )
            {
              for( unsigned int i = 0; i < _tagVarNames.size(); i++ )
                {
                  if ( line.find(_tagVarNames[i].Data()) != std::string::npos )
                    {
                      getline(myfile, line, ',');
                      l1 = line.find_first_of("[");
                      line = line.substr(l1+1,line.size());
                      _tagVarRD.push_back((Double_t)atof(line.c_str()));
                      getline(myfile, line, ']');
                      _tagVarRU.push_back((Double_t)atof(line.c_str()));
                    }
                }
            }

	  if ( line.find("TagOmega") != std::string::npos )
            {
              getline (myfile,line,']');
              while ( line.find_first_of("\"") < line.size() && line.find_first_of("\"") != 0 )
                {
                  l1 = line.find_first_of("\"");
                  tmp = line.substr(l1+1, line.size());
                  l2 = tmp.find_first_of("\"");
                  tmp = line.substr(l1+1,l2);
                  _tagOmegaVarNames.push_back(tmp);
                  line = line.substr(l1+l2+2,line.size());
                }
              if(_tagOmegaVarNames.size() != 0 ) { _tagOmegaVar = true; }
            }
	  if ( _tagVar == true )
            {
              for( unsigned int i = 0; i < _tagOmegaVarNames.size(); i++ )
                {
                  if ( line.find(_tagOmegaVarNames[i].Data()) != std::string::npos )
                    {
                      getline(myfile, line, ',');
                      l1 = line.find_first_of("[");
                      line = line.substr(l1+1,line.size());
                      _tagOmegaVarRD.push_back((Double_t)atof(line.c_str()));
                      getline(myfile, line, ']');
                      _tagOmegaVarRU.push_back((Double_t)atof(line.c_str()));
                    }
		}
	      if ( line.find("calibration_p0") != std::string::npos )
		{
		  getline(myfile, line, ',');
		  l1 = line.find_first_of("[");
		  line = line.substr(l1+1,line.size());
		  _p0.push_back((Double_t)atof(line.c_str()));
		  getline(myfile, line, ']');
		  _p0.push_back((Double_t)atof(line.c_str()));
		}
	      if ( line.find("calibration_p1") != std::string::npos )
		{
		  getline(myfile, line, ',');
		  l1 = line.find_first_of("[");
		  line = line.substr(l1+1,line.size());
		  _p1.push_back((Double_t)atof(line.c_str()));
		  getline(myfile, line, ']');
		  _p1.push_back((Double_t)atof(line.c_str()));
		}
	      if ( line.find("calibration_av") != std::string::npos )
                {
                  getline(myfile, line, ',');
                  l1 = line.find_first_of("[");
                  line = line.substr(l1+1,line.size());
                  _av.push_back((Double_t)atof(line.c_str()));
                  getline(myfile, line, ']');
                  _av.push_back((Double_t)atof(line.c_str()));
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
  _terrRange    = other._terrRange;
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

  _tagVarNames = other._tagVarNames;
  _tagVarRU = other._tagVarRU;
  _tagVarRD = other._tagVarRD;
  _tagVar  = other._tagVar;
  
  _tagOmegaVarNames = other._tagOmegaVarNames;
  _tagOmegaVarRU = other._tagOmegaVarRU;
  _tagOmegaVarRD = other._tagOmegaVarRD;
  _tagOmegaVar  = other._tagOmegaVar;
 
  _p0 = other._p0;
  _p1 = other._p1;
  _av = other._av;
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
  out<<"Time range: ("<<s._terrRange[0]<<","<<s._terrRange[1]<<"), variable name: "<<s._terrVar<<std::endl;
  out<<"Charge range: ("<<s._idRange[0]<<","<<s._idRange[1]<<"), variable name: "<<s._idVar<<std::endl;
  out<<"Momentum range: ("<<s._pRange[0]<<","<<s._pRange[1]<<"),  variable name: "<<s._pVar<<std::endl;
  out<<"Transverse momentum range: ("<<s._ptRange[0]<<","<<s._ptRange[1]<<"),  variable name: "<<s._ptVar<<std::endl;
  out<<"nTracks range: ("<<s._nTracksRange[0]<<","<<s._nTracksRange[1]<<"),  variable name: "<<s._nTracksVar<<std::endl;

  if( s._tagVar == true )
    {
      out<<"Tag variables"<<std::endl;
      for( unsigned int i = 0; i < s._tagVarNames.size(); i++ )
        {
          out<<"Range: ("<<s._tagVarRD[i]<<","<<s._tagVarRU[i]<<"), variable name: "<<s._tagVarNames[i]<<std::endl;
        }
    }

  if( s._tagOmegaVar == true )
    {
      out<<"TagOmega variables"<<std::endl;
      for( unsigned int i = 0; i < s._tagOmegaVarNames.size(); i++ )
        {
          out<<"Range: ("<<s._tagOmegaVarRD[i]<<","<<s._tagOmegaVarRU[i]<<"), variable name: "<<s._tagOmegaVarNames[i]<<std::endl;
        }
    }
  if ( s._tagVar == true )
    {
      out<<"Calibration:"<<std::endl;
      for( unsigned int i = 0; i < s._tagVarNames.size(); i++ )
        {
          out<<"p0: "<<s._p0[i]<<", p1: "<<s._p1[i]<<", average: "<<s._av[i]<<std::endl;
        }
    }
  
  if( s._addVar == true )
    {
      out<<"Additional variables"<<std::endl;
      for( unsigned int i = 0; i < s._addVarNames.size(); i++ )
	{
	  out<<"Range: ("<<s._addVarRD[i]<<","<<s._addVarRU[i]<<"), variable name: "<<s._addVarNames[i]<<std::endl;
	}
    }

  out<<"labX notation: "<<s._labX<<std::endl;
  out<<"PIDK bachelor: "<<s._PIDBach<<std::endl;
  out<<"PIDK child: "<<s._PIDChild<<std::endl;
  out<<"PIDK proton: "<<s._PIDProton<<std::endl;
  out<<"Additional data cuts: "<<s._addDataCuts<<std::endl;
  out<<"Additional MC cuts: "<<s._addMCCuts<<std::endl;

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
  if( var == "" )          { return range;             }
  if( var == _mVar)        { return _massBRange[1];    }
  if( var == _mDVar)       { return _massDRange[1];    }
  if( var == _tVar)        { return _timeRange[1];     } 
  if( var == _terrVar)     { return _terrRange[1];     }
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
  for ( unsigned int i = 0; i <_tagVarNames.size(); i++ )
    {
      if( var == _tagVarNames[i]) { return _tagVarRU[i]; }
    }
  for ( unsigned int i = 0; i <_tagOmegaVarNames.size(); i++ )
    {
      if( var == _tagOmegaVarNames[i]) { return _tagOmegaVarRU[i]; }
    }
  std::cout<<"range: "<<range<<std::endl;
  return range;
}

Double_t MDFitterSettings::GetRangeDown(TString var)
{
  Double_t range = 1234.456;
  if( var == "" )          { return range;             }
  if( var == _mVar)        { return _massBRange[0];    }
  if( var == _mDVar)       { return _massDRange[0];    }
  if( var == _tVar)        { return _timeRange[0];     }
  if( var == _terrVar)     { return _terrRange[0];     } 
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
  for ( unsigned int i =0; i <_tagVarNames.size(); i++ )
    {
      if( var == _tagVarNames[i]) { return _tagVarRD[i]; }
    }
  for ( unsigned int i =0; i <_tagOmegaVarNames.size(); i++ )
    {
      if( var == _tagOmegaVarNames[i]) { return _tagOmegaVarRD[i]; }
    }  
  std::cout<<"range: "<<range<<std::endl;
  return range;
}

std::vector <Double_t> MDFitterSettings::GetRange(TString var)
{
  std::vector <Double_t> range;
  range.push_back(1234.456);
  range.push_back(1234.456);

  if( var == "" )          { return range;          }
  if( var == _mVar)        { return _massBRange;    }
  if( var == _mDVar)       { return _massDRange;    }
  if( var == _tVar)        { return _timeRange;     }
  if( var == _terrVar)     { return _terrRange;     }
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
  for (unsigned int i =0; i <_tagVarNames.size(); i++ )
    {
      if( var == _tagVarNames[i])
        {
          range[0] = _tagVarRD[i];
          range[1] = _tagVarRU[i];
        }
    }
  for (unsigned int i =0; i <_tagOmegaVarNames.size(); i++ )
    {
      if( var == _tagVarNames[i])
        {
          range[0] = _tagOmegaVarRD[i];
          range[1] = _tagOmegaVarRU[i];
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
  std::cout<<"range = ("<<range0<<","<<range1<<")"<<std::endl;
  std::cout<<"var: "<<var<<std::endl;

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
  TCut id_cut = GetCut(_idVar, sideband);
  TCut pidk_cut = GetCut(_PIDVar, sideband);
 
  all_cut = massB_cut&&massD_cut&&time_cut&&terr_cut&&BDTG_cut&&nTr_cut&&p_cut&&pt_cut&&id_cut&&pidk_cut; 

  return all_cut;
}

Bool_t MDFitterSettings::CheckVarName( TString name ) {
  Bool_t check = false;

  if( name == _mVar) { check = true; }
  if( name == _mDVar) { check = true;  }
  if( name == _tVar) { check = true; }
  if( name == _terrVar) { check = true; }
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
  for(unsigned int i = 0; i<_tagVarNames.size(); i++ )
    {
      if( _tagVarNames[i] == name) { check = true; }
    }
  for(unsigned int i = 0; i<_tagOmegaVarNames.size(); i++ )
    {
      if( _tagOmegaVarNames[i] == name) { check = true; }
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
  names.push_back(_BDTGVar);
  names.push_back(_pVar);
  names.push_back(_ptVar);
  names.push_back(_nTracksVar);
  names.push_back(_idVar);

  for ( unsigned int i =0; i <_addVarNames.size(); i++ )
    {
      names.push_back(_addVarNames[i]);
    }
  
  for ( unsigned int i =0; i <_tagVarNames.size(); i++ )
    {
      names.push_back(_tagVarNames[i]);
    }

  for ( unsigned int i =0; i <_tagOmegaVarNames.size(); i++ )
    {
      names.push_back(_tagOmegaVarNames[i]);
    }
  
  return names;
}
