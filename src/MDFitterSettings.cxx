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
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/HistPID1D.h"
#include "TString.h"
#include "RooRealVar.h"
#include "RooArgSet.h"
#include "TNamed.h"
#include "TCut.h"
#include "TMath.h" 

#include <vector>
#include <fstream>

using namespace GeneralUtils;

MDFitterSettings::MDFitterSettings(const TString& name, const TString& title)
{
  TNamed(name,title);

  _weightDim = 0.0;
  _massShift.first = 0;
  _massShift.second = 0; 

  _data = ""; 

  _filePIDBacEff.first = "";
  _filePIDBacEff.second = "";
  _filePIDBacMisID.first = "";
  _filePIDBacMisID.second = "";
  _filePIDChildMisID.first = "";
  _filePIDChildMisID.second = "";
  _filePIDChildProtonMisID.first = "";
  _filePIDChildProtonMisID.second = "";

  _PIDBacEff.first = ""; _PIDBacEff.second = "";
  _PIDBacMisID.first = ""; _PIDBacMisID.second = "";
  _PIDChildMisID.first = ""; _PIDChildMisID.second = "";
  _PIDChildProtonMisID.first = ""; _PIDChildProtonMisID.second = "";

  _ratioDMC.first = ""; _ratioDMC.second = ""; 

  for(int i = 0; i< 2; i++ )
    {
      std::vector<Double_t> row;
      for ( int j = 0; j<2; j++)
	{
	  row.push_back(-1.0);
	}
      _lumRatio.push_back(row);
      _lumFlag.push_back(false); 
    }

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
      //_calibPion.push_back("");
      //_calibKaon.push_back("");
      //_calibProton.push_back("");
      //_calibCombo.push_back(""); 
      _prefixDsChild.push_back(""); 
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

  _mVarOut = "";
  _mDVarOut = "";
  _tVarOut = "";
  _terrVarOut = "";
  _idVarOut = "";
  _PIDVarOut = "";
  _BDTGVarOut = "";
  _nTracksVarOut = "";
  _pVarOut = "";
  _ptVarOut = "";

  _addVar = false;
  _tagVar = false;
  _tagOmegaVar = false;
  _weightMassTemp = false;
  _weightRatioDataMC = false;

  for(int i = 0; i < 10; i ++ )
    {
      _addDataCuts.push_back(""); 
      _addMCCuts.push_back(""); 
      _addIDCuts.push_back(0);
      _addTRUEIDCuts.push_back(0);
      _addBKGCATCuts.push_back(0);
      _addDsHypoCuts.push_back(0); 
    }

  _addModeCuts.push_back("All");
  _addModeCuts.push_back("kkpi");
  _addModeCuts.push_back("kpipi");
  _addModeCuts.push_back("pipipi");
  _addModeCuts.push_back("phipi"); 
  _addModeCuts.push_back("nonres");
  _addModeCuts.push_back("kstk");
  _addModeCuts.push_back("hhhpi0");

  _calibCombo = false; 
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

  _lumRatio = other._lumRatio;
  _weightDim = other._weightDim;
  _calib   = other._calib;
  _calibCombo = other._calibCombo; 

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

  _ratioDMC = other._ratioDMC; 
  _filePIDBacEff = other._filePIDBacEff;
  _filePIDBacMisID = other._filePIDBacMisID;
  _filePIDChildMisID = other._filePIDChildMisID;
  _filePIDChildProtonMisID = other._filePIDChildProtonMisID;
  
  _PIDBacEff = other._PIDBacEff;
  _PIDBacMisID = other._PIDBacMisID;
  _PIDChildMisID = other._PIDChildMisID;
  _PIDChildProtonMisID = other._PIDChildProtonMisID;

  _massShift = other._massShift; 

}

MDFitterSettings::~MDFitterSettings() { }

std::ostream & operator<< (std::ostream &out, const MDFitterSettings &s)
{
  out<<"==================================================================="<<std::endl;
  out<<"MDFitterSettings("<<s.GetName()<<","<<s.GetTitle()<<")"<<std::endl;
  out<<"==================================================================="<<std::endl;
  out<<"-------------------------------------------------------------------"<<std::endl;
  out<<"\t Basic variables: "<<std::endl;
  out<<"-------------------------------------------------------------------"<<std::endl;

  if ( s._mVar != "")  { out<<"B(s) mass range: ("<<s._massBRange[0]<<","<<s._massBRange[1]<<"), input name: "<<s._mVar<<", output name: "<<s._mVarOut<<std::endl;}
  if ( s._mDVar != "") { out<<"D(s) mass range: ("<<s._massDRange[0]<<","<<s._massDRange[1]<<"), input name: "<<s._mDVar<<", output name: "<<s._mDVarOut<<std::endl;}
  if ( s._PIDVar != "") { out<<"PIDK range: ("<<s._PIDRange[0]<<","<<s._PIDRange[1]<<"),  input name: "<<s._PIDVar<<", output name: "<<s._PIDVarOut<<std::endl; }
  if ( s._BDTGVar != "") { out<<"BDTG range: ("<<s._BDTGRange[0]<<","<<s._BDTGRange[1]<<"), input name: "<<s._BDTGVar<<", output name: "<<s._BDTGVarOut<<std::endl; }
  if ( s._tVar != "" ) { out<<"Time range: ("<<s._timeRange[0]<<","<<s._timeRange[1]<<"), input name: "<<s._tVar<<", output name: "<<s._tVarOut<<std::endl;}
  if ( s._terrVar != "" ) { out<<"Time range: ("<<s._terrRange[0]<<","<<s._terrRange[1]<<"), input name: "<<s._terrVar<<", output name: "<<s._terrVarOut<<std::endl;}
  if ( s._idVar != "") { out<<"Charge range: ("<<s._idRange[0]<<","<<s._idRange[1]<<"), input name: "<<s._idVar<<", output name: "<<s._idVarOut<<std::endl;}
  if ( s._pVar != "" ) { out<<"Momentum range: ("<<s._pRange[0]<<","<<s._pRange[1]<<"), intput name: "<<s._pVar<<", output name: "<<s._pVarOut<<std::endl;}
  if ( s._ptVar != "") { out<<"Transverse momentum range: ("<<s._ptRange[0]<<","<<s._ptRange[1]<<"),  variable name: "<<s._ptVar<<", output name: "<<s._ptVarOut<<std::endl;}
  if ( s._nTracksVar != "") { out<<"nTracks range: ("<<s._nTracksRange[0]<<","<<s._nTracksRange[1]<<"),  variable name: "<<s._nTracksVar<<", output name: "<<s._nTracksVarOut<<std::endl;}

  out<<"-------------------------------------------------------------------"<<std::endl;
  out<<"\t Tagging: "<<std::endl;
  out<<"-------------------------------------------------------------------"<<std::endl;

  if( s._tagVar == true )
    {
      out<<"Tagging decision variables"<<std::endl;
      for( unsigned int i = 0; i < s._tagVarNames.size(); i++ )
        {
          out<<"Range: ("<<s._tagVarRD[i]<<","<<s._tagVarRU[i]<<"), input name: "<<s._tagVarNames[i]<<", output name: "<<s._tagVarNamesOut[i]<<std::endl;
        }
    }

  if( s._tagOmegaVar == true )
    {
      out<<"Tagging mistag variables"<<std::endl;
      for( unsigned int i = 0; i < s._tagOmegaVarNames.size(); i++ )
        {
          out<<"Range: ("<<s._tagOmegaVarRD[i]<<","<<s._tagOmegaVarRU[i]
	     <<"), variable name: "<<s._tagOmegaVarNames[i]
	     <<", output name: "<<s._tagOmegaVarNamesOut[i]<<std::endl;
        }
    }
  if ( s._tagVar == true )
    {
      out<<"Tagging calibration:"<<std::endl;
      for( unsigned int i = 0; i < s._tagVarNames.size(); i++ )
        {
          out<<"\t "<<s._matchTag[i]<<": p0: "<<s._p0[i]<<", p1: "<<s._p1[i]<<", average: "<<s._av[i]<<" use: "<<s._useTag[i]<<std::endl;
        }
    }

  out<<"-------------------------------------------------------------------"<<std::endl;
  out<<"\t Additional cuts applied to data set: "<<std::endl;
  out<<"-------------------------------------------------------------------"<<std::endl;

  TString mode[] = {"All","KKPi","KPiPi","PiPiPi","NonRes","KstK","PhiPi","HHHPi0"}; 
  for (int i= 0; i<10; i++)
    {
      if(s._addDataCuts[i] != "" || s._addMCCuts[i] != "" )
	{
	  if( i == 0 )
	    {
	      out<<"Additional cuts for "<<mode[i]<<std::endl;
	      out<<"\t Data: "<<s._addDataCuts[i]<<std::endl;
	      out<<"\t MC: "<<s._addMCCuts[i]<<std::endl; 
	    }
	  else
	    {
	      TString cD = "";
	      TString cMC = "";
	      if( s._addDataCuts[0] != "" ) { cD = s._addDataCuts[0]+"&&"+s._addDataCuts[i]; } else { cD = s._addDataCuts[i]; }
	      if( s._addMCCuts[0] != "" ) { cMC = s._addMCCuts[0]+"&&"+s._addMCCuts[i]; } else { cMC = s._addMCCuts[i]; }
	      out<<"Additional cuts for "<<mode[i]<<std::endl;
	      out<<"\t Data: "<<cD<<std::endl;
	      out<<"\t MC: "<<cMC<<std::endl;
	    }
	}
    }

  if( s._addVar == true )
    {
  
     
      out<<"-------------------------------------------------------------------"<<std::endl;
      out<<"\t Additional variables in data set: "<<std::endl;
      out<<"-------------------------------------------------------------------"<<std::endl;

      for( unsigned int i = 0; i < s._addVarNames.size(); i++ )
	{
	  out<<"Range: ("<<s._addVarRD[i]<<","<<s._addVarRU[i]<<"), input name: "<<s._addVarNames[i]<<" output name: "<<s._addVarNamesOut[i]<<std::endl;
	}
    }

  if ( s._weightMassTemp == true )
    {
      out<<"-------------------------------------------------------------------"<<std::endl;
      out<<"\t Mass templates will be weighted using following settings: "<<std::endl;
      out<<"-------------------------------------------------------------------"<<std::endl;

      out<<" Shift for "<<s._mVarOut<<" is: "<<s._massShift.first<<std::endl;
      out<<" Shift for "<<s._mDVarOut<<" is: "<<s._massShift.second<<std::endl;
      out<<" Bachelor Efficinecy: "<<std::endl;
      out<<" \t file for 2011: "<<s._filePIDBacEff.first<<std::endl;
      out<<" \t file for 2012: "<<s._filePIDBacEff.second<<std::endl;
      out<<" \t name of histogram: "<<s._PIDBacEff.first<<std::endl;
      out<<" \t variable weighted: "<<s._PIDBacEff.second<<std::endl;
      out<<"-------------------------------------------------------------------"<<std::endl;
      out<<" Bachelor MisID: "<<std::endl;
      out<<" \t file for 2011: "<<s._filePIDBacMisID.first<<std::endl;
      out<<" \t file for 2012: "<<s._filePIDBacMisID.second<<std::endl;
      out<<" \t name of histogram: "<<s._PIDBacMisID.first<<std::endl;
      out<<" \t variable weighted: "<<s._PIDBacMisID.second<<std::endl;
      out<<"-------------------------------------------------------------------"<<std::endl;
      out<<" Kaon/Pion MisID: "<<std::endl;
      out<<" \t file for 2011: "<<s._filePIDChildMisID.first<<std::endl;
      out<<" \t file for 2012: "<<s._filePIDChildMisID.second<<std::endl;
      out<<" \t name of histogram: "<<s._PIDChildMisID.first<<std::endl;
      out<<" \t variable weighted: "<<s._PIDChildMisID.second<<std::endl;
      out<<"-------------------------------------------------------------------"<<std::endl;
      out<<" Proton MisID: "<<std::endl;
      out<<" \t file for 2011: "<<s._filePIDChildProtonMisID.first<<std::endl;
      out<<" \t file for 2012: "<<s._filePIDChildProtonMisID.second<<std::endl;
      out<<" \t name of histogram: "<<s._PIDChildProtonMisID.first<<std::endl;
      out<<" \t variable weighted: "<<s._PIDChildProtonMisID.second<<std::endl;
      out<<"-------------------------------------------------------------------"<<std::endl;
      out<<"-------------------------------------------------------------------"<<std::endl;
      out<<" Ratio data MC: "<<s._weightRatioDataMC<<std::endl;
      out<<" \t label for 2011: "<<s._ratioDMC.first<<std::endl;
      out<<" \t label for 2012: "<<s._ratioDMC.second<<std::endl; 
      out<<"-------------------------------------------------------------------"<<std::endl;
      //      out<<"PIDK bachelor: "<<s._PIDBach<<std::endl;
      //out<<"PIDK child: "<<s._PIDChild<<std::endl;
      //out<<"PIDK proton: "<<s._PIDProton<<std::endl;
      //if (s._weightMassTempVar.size() > 0 )
      //	{
      //	  out<<"Variables: ";
      //  for (unsigned int i = 0; i<s._weightMassTempVar.size(); i++)
      //    {
      //      out<<s._weightMassTempVar[i]<<" "; 
      //    }
      //  out<<std::endl;
      //	}
      out<<"Prefix for Ds children: "<<s._prefixDsChild[0]<<" "<<s._prefixDsChild[1]<<" "<<s._prefixDsChild[2]<<std::endl;
    }

  if ( s._weightDim != 0 )
    {
     
      //out<<std::endl;
      out<<"-------------------------------------------------------------------"<<std::endl;
      out<<"\t PIDK weighting details: "<<std::endl;
      out<<"-------------------------------------------------------------------"<<std::endl;

      out<<"weighting dimensions: "<<s._weightDim<<std::endl;
      if ( s._bin.size() > 0 )
	{
	  out<<"Bin: ";
	  for (unsigned int i = 0; i<s._bin.size(); i++)
	    {
	      out<<s._bin[i]<<" ";
	    }
	  out<<std::endl;
	}
      if ( s._var.size() > 0 )
	{
	  out<<"Var: ";
	  for (unsigned int i = 0; i<s._var.size(); i++)
	    {
	      out<<s._var[i]<<" ";
	    }
	  out<<std::endl;
	}

      for(unsigned int i = 0; i < s._calib.size(); i++ )
	{
	  out<<s._calib[i]<<std::endl; 
	}
      if ( s._calibCombo == true ) { std::cout<<"[INFO] Combinatorial calibration samples will be taken from recent workspace"<<std::endl; }
      /*
      if( s._calibPion[0] != "" ||  s._calibPion[1] != "" ||  s._calibPion[2] != "") { out<<"pion calibration sample: "<<std::endl;}
      if ( s._calibPion[0] != "" ) { out<<"\t up file: "<<s._calibPion[0]<<std::endl; }
      if ( s._calibPion[1] != "" ) { out<<"\t down file: "<<s._calibPion[1]<<std::endl;}
      if ( s._calibPion[2] != "" ) { out<<"\t workspace name: "<<s._calibPion[2]<<std::endl;}
      
      if( s._calibKaon[0] != ""||  s._calibKaon[1] != "" ||  s._calibKaon[2] != "") { out<<"kaon calibration sample: "<<std::endl;}
      if( s._calibKaon[0] != "" ) { out<<"\t up file: "<<s._calibKaon[0]<<std::endl;}
      if( s._calibKaon[1] != "" ) { out<<"\t down file: "<<s._calibKaon[1]<<std::endl;}
      if( s._calibKaon[2] != "" ) { out<<"\t workspace name: "<<s._calibKaon[2]<<std::endl;}
      
      if( s._calibProton[0] != ""||  s._calibProton[1] != "" ||  s._calibProton[2] != "") { out<<"proton calibration sample: "<<std::endl;}
      if( s._calibProton[0] != "" ) { out<<"\t up file: "<<s._calibProton[0]<<std::endl;}
      if( s._calibProton[1] != "" ) { out<<"\t down file: "<<s._calibProton[1]<<std::endl;}
      if( s._calibProton[2] != "" ) { out<<"\t workspace name: "<<s._calibProton[2]<<std::endl;}
      */
      if ( s._lumFlag[0] == true || s._lumFlag[1] == true ) { out<<"Luminosity: "<<std::endl;}
      if ( s._lumFlag[0] == true ) { out<<"2011 (MD,MU)=("<<s._lumRatio[0][0]<<","<<s._lumRatio[0][1]<<")"<<std::endl;}
      if ( s._lumFlag[1] == true ) { out<<"2012 (MD,MU)=("<<s._lumRatio[1][0]<<","<<s._lumRatio[1][1]<<")"<<std::endl; }
    }
  return out;
}

Double_t MDFitterSettings::GetRangeUp(TString var)
{
  Double_t range = 1234.456;
  if( var == "" )          { return range;             }
  if( var == _mVar        || var == _mVarOut )        { return _massBRange[1];    }
  if( var == _mDVar       || var == _mDVarOut )       { return _massDRange[1];    }
  if( var == _tVar        || var == _tVarOut )        { return _timeRange[1];     } 
  if( var == _terrVar     || var == _terrVarOut )     { return _terrRange[1];     }
  if( var == _idVar       || var == _idVarOut )       { return _idRange[1];       }
  if( var == _PIDVar      || var == _PIDVarOut )      { return _PIDRange[1];      }
  if( var == _BDTGVar     || var == _BDTGVarOut )     { return _BDTGRange[1];     }
  if( var == _nTracksVar  || var == _nTracksVarOut )     { return _nTracksRange[1];  }
  if( var == _pVar        || var == _pVarOut )        { return _pRange[1];        }
  if( var == _ptVar       || var == _ptVarOut)        { return _ptRange[1];       }
  for ( unsigned int i = 0; i <_addVarNames.size(); i++ )
    {
      if( var == _addVarNames[i] || var == _addVarNamesOut[i]) { return _addVarRU[i]; }
    }
  for ( unsigned int i = 0; i <_tagVarNames.size(); i++ )
    {
      if( var == _tagVarNames[i] || var == _tagVarNamesOut[i]) { return _tagVarRU[i]; }
    }
  for ( unsigned int i = 0; i <_tagOmegaVarNames.size(); i++ )
    {
      if( var == _tagOmegaVarNames[i] || var == _tagOmegaVarNamesOut[i]) { return _tagOmegaVarRU[i]; }
    }
  //std::cout<<"range: "<<range<<std::endl;
  return range;
}

Double_t MDFitterSettings::GetRangeDown(TString var)
{
  Double_t range = 1234.456;
  if( var == "" )          { return range;             }
  if( var == _mVar        || var == _mVarOut )        { return _massBRange[0];    }
  if( var == _mDVar       || var == _mDVarOut )       { return _massDRange[0];    }
  if( var == _tVar        || var == _tVarOut )        { return _timeRange[0];     }
  if( var == _terrVar     || var == _terrVarOut )     { return _terrRange[0];     } 
  if( var == _idVar       || var == _idVarOut )       { return _idRange[0];       }
  if( var == _PIDVar      || var == _PIDVarOut )      { return _PIDRange[0];      }
  if( var == _BDTGVar     || var == _BDTGVarOut )     { return _BDTGRange[0];     }
  if( var == _nTracksVar  || var == _nTracksVarOut )  { return _nTracksRange[0];  }
  if( var == _pVar        || var == _pVarOut )        { return _pRange[0];        }
  if( var == _ptVar       || var == _ptVarOut )       { return _ptRange[0];       }
  for ( unsigned int i =0; i <_addVarNames.size(); i++ )
    {
      if( var == _addVarNames[i] || var == _addVarNamesOut[i]) { return _addVarRD[i]; }
    }
  for ( unsigned int i =0; i <_tagVarNames.size(); i++ )
    {
      if( var == _tagVarNames[i] || var == _tagVarNamesOut[i]) { return _tagVarRD[i]; }
    }
  for ( unsigned int i =0; i <_tagOmegaVarNames.size(); i++ )
    {
      if( var == _tagOmegaVarNames[i] ||  var == _tagOmegaVarNamesOut[i]) { return _tagOmegaVarRD[i]; }
    }  
  //std::cout<<"range: "<<range<<std::endl;
  return range;
}

std::vector <Double_t> MDFitterSettings::GetRange(TString var)
{
  std::vector <Double_t> range;
  range.push_back(1234.456);
  range.push_back(1234.456);

  if( var == "" )          { return range;          }
  if( var == _mVar        || var == _mVarOut )        { return _massBRange;    }
  if( var == _mDVar       || var == _mDVarOut )       { return _massDRange;    }
  if( var == _tVar        || var == _tVarOut )        { return _timeRange;     }
  if( var == _terrVar     || var == _terrVarOut )     { return _terrRange;     }
  if( var == _idVar       || var == _idVarOut )       { return _idRange;       }
  if( var == _PIDVar      || var == _PIDVarOut )      { return _PIDRange;      }
  if( var == _BDTGVar     || var == _BDTGVarOut )     { return _BDTGRange;     }
  if( var == _nTracksVar  || var == _nTracksVarOut )  { return _nTracksRange;  }
  if( var == _pVar        || var == _pVarOut )        { return _pRange;        }
  if( var == _ptVar       || var == _ptVarOut )       { return _ptRange;       }
  for (unsigned int i =0; i <_addVarNames.size(); i++ )
    {
      if( var == _addVarNames[i] || var == _addVarNamesOut[i]) 
	{
	  range[0] = _addVarRD[i];
	  range[1] = _addVarRU[i];
	}
    }
  for (unsigned int i =0; i <_tagVarNames.size(); i++ )
    {
      if( var == _tagVarNames[i] || var == _tagVarNamesOut[i] )
        {
          range[0] = _tagVarRD[i];
          range[1] = _tagVarRU[i];
        }
    }
  for (unsigned int i =0; i <_tagOmegaVarNames.size(); i++ )
    {
      if( var == _tagOmegaVarNames[i] ||  var == _tagOmegaVarNamesOut[i])
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
  //std::cout<<"range = ("<<range0<<","<<range1<<")"<<std::endl;
  //std::cout<<"var: "<<var<<std::endl;

  Float_t c = 299792458.0;
  Float_t corr = c/1e9;

  if ( sideband == false )
    {
      if( var.Contains("ctau") ==true || var.Contains("CTAU") == true )
	{
	  range0 = range0*corr;
	  range1 = range1*corr; 
	  
	  if ( range0 != 1234.456 )
	    {
	      cut1  = Form("%s[0] > %f", var.Data(), range0); 
	    }
	  
	  if ( range1 != 1234.456 )
	    {
	      cut2  = Form("%s[0] < %f", var.Data(), range1);
	    }
	}
      else
	{
	  if ( range0 != 1234.456 )
	    {
	      cut1  = Form("%s > %f", var.Data(), range0);
	    }

	  if ( range1 != 1234.456 )
	    {
	      cut2  = Form("%s < %f", var.Data(), range1);
	    }
	}
      cut = cut1&&cut2;
	
    }
  else
    {
      if( var.Contains("ctau") ==true || var.Contains("CTAU") == true )
	{
          range0 = range0*corr;
          range1 = range1*corr;
	  if ( range0 != 1234.456 )
	    {
	      cut1  = Form("%s[0] < %f", var.Data(), range0);
	    }
	  
	  if ( range1 != 1234.456 )
	    {
	      cut2  = Form("%s[0] > %f", var.Data(), range1);
	    }
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

Bool_t MDFitterSettings::CheckVarOutName( TString name ) {

Bool_t check = false;

if( name == _mVarOut) { check = true; }
if( name == _mDVarOut) { check = true;  }
if( name == _tVarOut) { check = true; }
if( name == _terrVarOut) { check = true; }
if( name == _idVarOut) { check = true; }
if( name == _PIDVarOut) { check = true; }
if( name == _BDTGVarOut) { check = true; }
if( name == _nTracksVarOut) { check = true; }
if( name == _pVarOut) { check = true; }
if( name == _ptVarOut) { check = true; }

for(unsigned int i = 0; i<_addVarNames.size(); i++ )
  {
    if( _addVarNamesOut[i] == name) { check = true; }
  }
for(unsigned int i = 0; i<_tagVarNames.size(); i++ )
  {
    if( _tagVarNamesOut[i] == name) { check = true; }
  }
for(unsigned int i = 0; i<_tagOmegaVarNames.size(); i++ )
  {
    if( _tagOmegaVarNamesOut[i] == name) { check = true; }
  }

return check;
}


TString MDFitterSettings::GetVarOutName(TString var)
{
  TString outName = "";
  if( var == "" )          { return outName;          }
  if( var == _mVar)        { return _mVarOut;    }
  if( var == _mDVar)       { return _mDVarOut;    }
  if( var == _tVar)        { return _tVarOut;     }
  if( var == _terrVar)     { return _terrVarOut;     }
  if( var == _idVar)       { return _idVarOut;       }
  if( var == _PIDVar)      { return _PIDVarOut;      }
  if( var == _BDTGVar)     { return _BDTGVarOut;     }
  if( var == _nTracksVar)  { return _nTracksVarOut;  }
  if( var == _pVar)        { return _pVarOut;        }
  if( var == _ptVar)       { return _ptVarOut;       }
  for (unsigned int i =0; i <_addVarNames.size(); i++ )
    {
      if( var == _addVarNames[i])
	{
          outName =  _addVarNamesOut[i];
        }
    }
  for (unsigned int i =0; i <_tagVarNames.size(); i++ )
    {
      if( var == _tagVarNames[i])
        {
          outName =  _tagVarNamesOut[i];
	}
    }

  for (unsigned int i =0; i <_tagOmegaVarNames.size(); i++ )
    {
      if( var == _tagOmegaVarNames[i])
        {
          outName =  _tagOmegaVarNamesOut[i];
        }
    }

  return outName;

}


RooRealVar* MDFitterSettings::GetObs(TString varName, bool inName, bool log)
{
  RooRealVar* Var = NULL;
  Bool_t check = CheckVarOutName(varName);
  if ( inName == true ) { check = CheckVarName(varName);}

  if ( check == true )
   { 
     
     Double_t range0 = GetRangeDown(varName);
     Double_t range1 = GetRangeUp(varName);
     TString  varOutName = "";
     if ( inName == true ) 
       {
	 varOutName = GetVarOutName(varName); 
       }
     else
       {
	 varOutName = varName; 
       }
      if ( range0 != 1234.456 && range1 != 1234.456)
	{
	  if( log == false )
	    {
	      //if ( inName == true && (varName.Contains("ctau") == true || varName.Contains("CTAU") == true ))
	      //{
	      //range0 = range0*corr;
	      //range1 = range1*corr;
	      //	}
	      Var = new RooRealVar(varOutName.Data(), varOutName.Data(), range0, range1);
	      //std::cout<<"[INFO] Create variable: "<<varOutName<<" with range: ["<<range0<<","<<range1<<"]"<<std::endl; 
	    }
	  else
	    {
	      //std::cout<<varOutName<<" "<<TMath::Log(range0)<<" "<<TMath::Log(range1)<<std::endl; 
	      Var = new RooRealVar(varOutName.Data(), varOutName.Data(), TMath::Log(range0), TMath::Log(range1));
	      //std::cout<<"[INFO] Create variable: "<<varOutName<<" with range: ["<<TMath::Log(range0)<<","<<TMath::Log(range1)<<"]"<<std::endl;
	    }
	}
    }
  return Var;
}

std::vector <TString> MDFitterSettings::GetVarNames(Bool_t reg, Bool_t id, Bool_t add, Bool_t tag, Bool_t tagOmega)
{
  std::vector <TString> names;
  if ( reg == true ) 
    {

      if ( _mVar != "") { names.push_back(_mVar);}
      if ( _mDVar != "") { names.push_back(_mDVar);}
      if ( _PIDVar != "") { names.push_back(_PIDVar);}
      if ( _tVar != "") { names.push_back(_tVar);}
      if ( _terrVar != "" ) { names.push_back(_terrVar);}
      if ( _BDTGVar != "" ) { names.push_back(_BDTGVar);}
      if ( _pVar != "" ) { names.push_back(_pVar);}
      if ( _ptVar != "") { names.push_back(_ptVar);}
      if ( _nTracksVar != "" ) { names.push_back(_nTracksVar);}
    }
  if ( id == true ) 
    {
      names.push_back(_idVar);
    }

  if (add == true )
    {
      for ( unsigned int i =0; i <_addVarNames.size(); i++ )
	{
	  names.push_back(_addVarNames[i]);
	}
    }
  if ( tag == true )
    {
      for ( unsigned int i =0; i <_tagVarNames.size(); i++ )
	{
	  names.push_back(_tagVarNames[i]);
	}
    }
  if ( tagOmega == true )
    {
      for ( unsigned int i =0; i <_tagOmegaVarNames.size(); i++ )
	{
	  names.push_back(_tagOmegaVarNames[i]);
	}
    }
  return names;
}

std::vector <TString> MDFitterSettings::GetVarOutNames(Bool_t reg, Bool_t id, Bool_t add, Bool_t tag, Bool_t tagOmega)
{
  std::vector <TString> names;
  if ( reg == true )
    {

      if ( _mVarOut != "") { names.push_back(_mVarOut);}
      if ( _mDVarOut != "") { names.push_back(_mDVarOut);}
      if ( _PIDVarOut != "") { names.push_back(_PIDVarOut);}
      if ( _tVarOut != "") { names.push_back(_tVarOut);}
      if ( _terrVarOut != "" ) { names.push_back(_terrVarOut);}
      if ( _BDTGVarOut != "" ) { names.push_back(_BDTGVarOut);}
      if ( _pVarOut != "" ) { names.push_back(_pVarOut);}
      if ( _ptVarOut != "") { names.push_back(_ptVarOut);}
      if ( _nTracksVarOut != "" ) { names.push_back(_nTracksVarOut);}
    }
  if ( id == true )
    {
      names.push_back(_idVarOut);
    }

  if (add == true )
    {
      for ( unsigned int i =0; i <_addVarNamesOut.size(); i++ )
	{
          names.push_back(_addVarNamesOut[i]);
        }
    }
  if ( tag == true )
    {
      for ( unsigned int i =0; i <_tagVarNamesOut.size(); i++ )
        {
          names.push_back(_tagVarNamesOut[i]);
        }
    }
  if ( tagOmega == true )
    {
      for ( unsigned int i =0; i <_tagOmegaVarNamesOut.size(); i++ )
        {
          names.push_back(_tagOmegaVarNamesOut[i]);
        }
    }
  return names;
}


TString MDFitterSettings::GetDataCuts(TString& mode)
{
  TString cut = ""; 
  TString Mode = "";
  if ( mode == "All" )
    {
      Mode = mode; 
    }
  else
    {
      Mode = CheckDMode(mode);
      if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
    }

  if ( _addDataCuts[0] !="" )
    {
      cut = _addDataCuts[0];
      if( Mode == "All" ) { return cut; }
      else
	{
	  for(int i = 0; i<10; i++)
            {
              if ( Mode == _addModeCuts[i] && _addDataCuts[i] != "")
                {
                  cut += "&&"+_addDataCuts[i];
                }
            }
	  if ( (Mode == "phipi" || Mode == "nonres" || Mode == "kstk" )&& _addMCCuts[1] != "" )
            {
	      cut += "&&"+_addMCCuts[1];
            }
	}
    }
  else
    {
      for(int i = 0; i<10; i++)
	{
	  if ( Mode == _addModeCuts[i] && _addDataCuts[i] != "")
	    {
	      cut = _addDataCuts[i];
	    }
	}
    }
  return cut;
}

TString MDFitterSettings::GetMCCuts(TString& mode)
{
  TString cut = "";
  TString Mode = "";
  if ( mode == "All" || mode == "all" || mode == "ALL")
    {
      Mode = "All";
    }
  else
    {
      Mode = CheckDMode(mode);
      if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
    }

  if ( _addMCCuts[0] != "" ) 
    {
      cut = _addMCCuts[0];
      if( Mode == "All" ) { return cut; }
      else
	{
	  for(int i = 0; i<10; i++)
	    {
	      if ( Mode == _addModeCuts[i] && _addMCCuts[i] != "")
		{
		  cut += "&&"+_addMCCuts[i]; 
		}
	    }
	  if ( (Mode == "phipi" || Mode == "nonres" || Mode == "kstk" ) && _addMCCuts[1] != "" )
	    {
	      cut += "&&"+_addMCCuts[1];
	    }
	}
    }
  else
    {
      for(int i = 0; i<10; i++)
        {
          if ( Mode == _addModeCuts[i] && _addMCCuts[i] != "")
            {
              cut = _addMCCuts[i];
            }
        }
    }
  return cut; 
}


void MDFitterSettings::SetMCCuts(TString mode, TString cut)
{
  TString Mode = "";
  if (  mode == "All" || mode == "all" || mode == "ALL" )
    {
      Mode = "All";
    }
  else
    {
      Mode = CheckDMode(mode);
      if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
      //std::cout<<"!!!!!!!!!!!!!!!!!!!!! Mode: "<<Mode<<std::endl; 
    }

  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
        {
          _addMCCuts[i] = cut;
        }
    }
}

void MDFitterSettings::SetDataCuts(TString mode, TString cut)
{
  TString Mode = "";
  if ( mode == "All" || mode == "all" || mode == "ALL" )
    {
      Mode = "All";
    }
  else
    {
      Mode = CheckDMode(mode);
      if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
      //std::cout<<"!!!!!!!!!!!!!!!!!!!!! Mode: "<<Mode<<std::endl;
    }

  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
        {
          _addDataCuts[i] = cut;
	}
    }
}

void MDFitterSettings::SetIDCut(TString mode, Bool_t cut)
{
  TString Mode = "";
  if ( mode == "All" || mode == "all" || mode == "ALL" )
    {
      Mode = "All";
    }
  else
    {
      Mode = CheckDMode(mode);
      if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
    }

  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
        {
          _addIDCuts[i] = cut;
        }
    }

}

void MDFitterSettings::SetTRUEIDCut(TString mode, Bool_t cut)
{
  TString Mode = "";
  if ( mode == "All" || mode == "all" || mode == "ALL" )
    {
      Mode = "All";
    }
  else
    {
      Mode = CheckDMode(mode);
      if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
    }

  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
        {
          _addTRUEIDCuts[i] = cut;
        }
    }
}

void MDFitterSettings::SetBKGCATCut(TString mode, Bool_t cut)
{
  TString Mode = "";
  if ( mode == "All" || mode == "all" || mode == "ALL" )
    {
      Mode = "All";
    }
  else
    {
      Mode = CheckDMode(mode);
      if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
    }

  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
        {
          _addBKGCATCuts[i] = cut;
        }
    }

}
void MDFitterSettings::SetDsHypoCut(TString mode, Bool_t cut)
{
  TString Mode = "";
  if ( mode == "All" || mode == "all" || mode == "ALL" )
    {
      Mode = "All";
    }
  else
    {
      Mode = CheckDMode(mode);
      if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
    }

  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
        {
          _addDsHypoCuts[i] = cut;
        }
    }
}


TString MDFitterSettings::GetPrefix(TString name)
{
  TString prefix = name;
  Ssiz_t l = prefix.First("_");
  if ( l != -1 )
    {
      prefix.Remove(l);
    }
  else
    {
      prefix = "";
    }
  return prefix;
}

Bool_t MDFitterSettings::CheckIDCut(TString& mode)
{
  if ( _addIDCuts[0] == 1 ) { return true; }
  Bool_t cut = false; 
  TString Mode = "";
  Mode = CheckDMode(mode);
  if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
	{
	  if ( _addIDCuts[i] == 1 ) { return true; }
	}
    }
  if ( (Mode == "phipi" || Mode == "nonres" || Mode == "kstk" ) && _addIDCuts[1] == 1 )
    {
      return true;
    }
  if ( cut == true )
    {
      if ( _prefixDsChild[0] != "" && _prefixDsChild[1] != "" && _prefixDsChild[2] != "" )
	{
	  return cut; 
	}
      else
	{
	  std::cout<<"[ERROR] Cannot set MC ID cuts without prefixes to Ds children. Please use configdict[\"DsChildrenPrefix\"] = {} in your config file."<<std::endl; 
	}   
    }
  return cut; 
   
}

Bool_t MDFitterSettings::CheckTRUEIDCut(TString& mode)
{

  if ( _addTRUEIDCuts[0] == 1 ) { return true; }
  Bool_t cut = false;
  TString Mode = "";
  Mode = CheckDMode(mode);
  if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
        {
          if ( _addTRUEIDCuts[i] == 1 ) { return true; }
        }
    }
  if ( (Mode == "phipi" || Mode == "nonres" || Mode == "kstk" ) && _addTRUEIDCuts[1] == 1 )
    {
      return true;
    }

  if ( cut == true )
    {
      if ( _prefixDsChild[0] != "" && _prefixDsChild[1] != "" && _prefixDsChild[2] != "" )
        {
	  return cut;
        }
      else
        {
	  std::cout<<"[ERROR] Cannot set MC ID cuts without prefixes to Ds children. Please use configdict[\"DsChildrenPrefix\"] = {} in your config file."<<std::endl;
        }
    }
  return cut;

}

Bool_t MDFitterSettings::CheckBKGCATCut(TString& mode)
{
  if ( _addBKGCATCuts[0] == 1 ) { return true; }
  Bool_t cut = false;
  TString Mode = "";
  Mode = CheckDMode(mode);
  if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
        {
          if ( _addBKGCATCuts[i] == 1 ) { return true; }
        }
    }
  if ( (Mode == "phipi" || Mode == "nonres" || Mode == "kstk" ) && _addBKGCATCuts[1] == 1 )
    {
      return true;
    }
  return cut; 
}

Bool_t MDFitterSettings::CheckDsHypoCut(TString& mode)
{
  if ( _addDsHypoCuts[0] == 1 ) { return true; }
  Bool_t cut = false;
  TString Mode = "";
  Mode = CheckDMode(mode);
  if ( Mode == ""){ Mode = CheckKKPiMode(mode);}
  for(int i = 0; i<10; i++)
    {
      if ( Mode == _addModeCuts[i] )
        {
          if ( _addDsHypoCuts[i] == 1 ) { return true; }
        }
    }
  if ( (Mode == "phipi" || Mode == "nonres" || Mode == "kstk" ) && _addDsHypoCuts[1] ==1 )
    {
      return true;
    }

  return cut;
}

RooArgSet* MDFitterSettings::GetObsSet(bool inName, bool regular, bool id, bool add, bool tag, bool tagomega)
{
  RooArgSet* obs = new RooArgSet();
  std::vector <RooRealVar*> obsReg;
  std::vector <TString> tN;
  if ( inName == true ) { tN = this->GetVarNames(true,false,false,false,false); }
  else { tN = this->GetVarOutNames(true,false,false,false,false); }
  if ( regular == true )
    {
      for(unsigned int i = 0; i < tN.size(); i++)
	{
	  //std::cout<<"[INFO] tN: "<<tN[i]<<std::endl; 
	  if ( tN[i] == _nTracksVar || tN[i] == _pVar || tN[i] == _ptVar 
	       || tN[i] == _nTracksVarOut || tN[i] == _pVarOut || tN[i] == _ptVarOut)
	    {
	      obsReg.push_back(this->GetObs(tN[i],inName,true));
	    }
	  else
	    {
	      obsReg.push_back(this->GetObs(tN[i],inName));
	    }
	  obs->add(*obsReg[i]); 
	}
    }
  RooCategory* obsCat = NULL; 
  if ( id == true )
    {
      TString name = "";
      if ( inName == true )
	{
	  name = _idVar;
	}
      else
	{
	  name = _idVarOut;
	}
      obsCat = new RooCategory(name.Data(), "bachelor charge");
      obsCat->defineType("h+",  1);
      obsCat->defineType("h-", -1);
      obs->add(*obsCat); 
    }
  
  std::vector <RooRealVar*> addVar;
  if ( add == true && this->CheckAddVar() == true )
    {
      for(int i = 0; i<this->GetNumAddVar(); i++)
	{
	   
	  TString name = "";
	  if ( inName == true ) { name = _addVarNames[i]; }
	  else { name = _addVarNamesOut[i]; } 
	  addVar.push_back(this->GetObs(name,inName));
	  obs->add(*addVar[i]); 
	}
    }
 
  std::vector <RooCategory*> tagObs;
  if( tag == true && _tagVar == true )
    {
      for(int i = 0; i<this->GetNumTagVar(); i++)                                                                                                                                        
	{                     
	  TString name = "";
	  if ( inName == true )
	    {
	      name = _tagVarNames[i];
	    }
	  else
	    {
	      name = _tagVarNamesOut[i]; 
	    }
	  tagObs.push_back(new RooCategory(name.Data(), "flavour tagging result"));                                                                       
	  TString BName = Form("B_%d",i);                                                                                                                                         
	  TString BbarName = Form("Bbar_%d",i);                                                                                                                                  
	  TString UnName = Form("Utagged_%d",i);                                                                                                                               
	  tagObs[i]->defineType(BName.Data(),     1);                                                                                                                            
	  tagObs[i]->defineType(BbarName.Data(), -1);                                                                                                                              
	  tagObs[i]->defineType(UnName.Data(),    0);                                                                                                                        
	  obs->add(*tagObs[i]); 
	}                                                                                                                                                                         
    }
  
  std::vector <RooRealVar*> tagOmegaObs;
  if ( tagomega == true && _tagOmegaVar == true )
    {
      for(int i = 0; i<this->GetNumTagOmegaVar(); i++)                                                                                                                            
	{ 
	  TString name = "";
          if ( inName == true ) { name = this->GetTagOmegaVar(i); }
          else { name = this->GetTagOmegaVarOutName(i); }
	
	  tagOmegaObs.push_back(this->GetObs(name,inName));                                                                                                   
	  obs->add(*tagOmegaObs[i]);
	}
    }

  return obs;
}




void MDFitterSettings::SetMassB( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{
  _mVar = inName; 
  _mVarOut = outName; 
  _massBRange[0] = range_down;     
  _massBRange[1] = range_up;
}

void MDFitterSettings::SetMassD( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{
  _mDVar = inName;
  _mDVarOut = outName;
  _massDRange[0] = range_down;
  _massDRange[1] = range_up;
}

void MDFitterSettings::SetTime( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{
  _tVar        = inName;
  _tVarOut        = outName;
  _timeRange[0] = range_down;      
  _timeRange[1] = range_up; 
}

void MDFitterSettings::SetMom( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{
  _pVar   = inName;
  _pVarOut   = outName;
  _pRange[0] = range_down;         
  _pRange[1] = range_up;
}

void MDFitterSettings::SetTrMom( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{
  _ptVar      = inName;
  _ptVarOut      = outName;
  _ptRange[0] = range_down;        
  _ptRange[1] = range_up;
}

void MDFitterSettings::SetTracks( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{
  
  _nTracksVar           = inName; 
  _nTracksVarOut           = outName;
  _nTracksRange[0] = range_down;   
  _nTracksRange[1] = range_up;
}

void MDFitterSettings::SetBDTG( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{

  _BDTGVar      = inName;
  _BDTGVarOut      = outName;
  _BDTGRange[0] = range_down;      
  _BDTGRange[1] = range_up;
}

void MDFitterSettings::SetPIDK( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{
  _PIDVar      = inName;
  _PIDVarOut      = outName;
  _PIDRange[0] = range_down;       
  _PIDRange[1] = range_up;
}

void MDFitterSettings::SetTerr( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{
  _terrVar      = inName;
  _terrVarOut      = outName;
  _terrRange[0] = range_down;      
  _terrRange[1] = range_up;  
}

void MDFitterSettings::SetID( TString inName, TString outName, Double_t range_down, Double_t range_up  )
{
  _idVar      = inName;
  _idVarOut      = outName;
  _idRange[0] = range_down;        
  _idRange[1] = range_up;
}

void MDFitterSettings::SetTag( TString inName, TString outName, Double_t range_down, Double_t range_up, int i )
{
  _tagVarNames[i] = inName;
  _tagVarNamesOut[i] = outName;
  _tagVarRD[i] = range_down;     
  _tagVarRU[i] = range_up;
}

void MDFitterSettings::SetTagOmega( TString inName, TString outName, Double_t range_down, Double_t range_up, int i )
{
  _tagOmegaVarNames[i] = inName;
  _tagOmegaVarNamesOut[i] = outName;
  _tagOmegaVarRD[i] = range_down; 
  _tagOmegaVarRU[i] = range_up;
}


void MDFitterSettings::SetLum(TString year, Double_t md, Double_t mu)
{
  Int_t i = -1;
  
  if ( year == "2011" ) { i = 0; } else if ( year == "2012" ) { i = 1; }
 
  if ( i != -1 )
    {
      _lumRatio[i][0] = md;
      _lumRatio[i][1] = mu;
      _lumFlag[i] = true; 
    }
  else
    {
      std::cout<<"[ERROR] Wrong year."<<std::endl; 
    }
}

Double_t MDFitterSettings::GetLum(TString year, TString pol)
{
  Int_t i = -1;
  Int_t j = -1;

  if ( year == "2011" ){ i = 0; } else if ( year == "2012" ) {i = 1; }
  if ( pol == "Down" ||pol == "MD" || pol == "down" || pol == "dw" ) { j = 0; }
  else if ( pol== "Up"|| pol == "MU" || pol =="up" ) { j = 1;}

  if ( i != -1 && j != -1 )
    {
      return _lumRatio[i][j];
    }
  else
    {
      std::cout<<"[ERROR] Wrong year or polarity"<<std::endl;
    }

  return 0; 
}

std::vector <Double_t> MDFitterSettings::GetLumRatio(TString check)
{
  std::vector <Double_t> lumRat;
  
  if ( check == "2011" || check == "2012" )
    {
      Int_t i = -1;
      if ( check == "2011" ){ i = 0; } else if ( check == "2012" ) {i = 1; }
      Double_t r1 = _lumRatio[i][0]/(_lumRatio[i][0]+_lumRatio[i][1]);
      Double_t r2 = _lumRatio[i][1]/(_lumRatio[i][0]+_lumRatio[i][1]);
      lumRat.push_back(r1);
      lumRat.push_back(r2); 
    }
  else if ( check == "Run1" || check == "run1") 
    {
      Double_t r2011 = _lumRatio[0][0]+_lumRatio[0][1];
      Double_t r2012 = _lumRatio[1][0]+_lumRatio[1][1];
      Double_t r1 = r2011 / ( r2011 + r2012 );
      Double_t r2 = r2012 / ( r2011 + r2012 ); 
      lumRat.push_back(r1);
      lumRat.push_back(r2);
    }
  else if ( check == "down" || check == "Down" || check == "Dw" || check == "dw") 
    {
      Double_t r1 = _lumRatio[0][0]/(_lumRatio[0][0]+_lumRatio[1][0]);
      Double_t r2 = _lumRatio[1][0]/(_lumRatio[0][0]+_lumRatio[1][0]);
      lumRat.push_back(r1);
      lumRat.push_back(r2);
    }
  else if ( check == "up" || check == "Up" )
    {
      Double_t r1 = _lumRatio[0][1]/(_lumRatio[0][1]+_lumRatio[1][1]);
      Double_t r2 = _lumRatio[1][1]/(_lumRatio[0][1]+_lumRatio[1][1]);
      lumRat.push_back(r1);
      lumRat.push_back(r2);
    }
  else
    {
      std::cout<<"[ERROR] Year incorrectly assigned."<<std::endl; 
    }
  return lumRat; 
  
}


void MDFitterSettings::SetPIDProperties(TString key, TString file2011, TString file2012, TString var, TString histName)
{
  if ( key == "PIDBachEff") 
    {
      _filePIDBacEff.first = file2011;
      _filePIDBacEff.second = file2012;
      _PIDBacEff.first = histName;
      _PIDBacEff.second = var; 
    }
  else if ( key == "PIDBachMisID") 
    {
      _filePIDBacMisID.first =file2011;
      _filePIDBacMisID.second = file2012;
      _PIDBacMisID.first = histName;
      _PIDBacMisID.second= var;
    }
  else if ( key == "PIDChildKaonPionMisID") 
    {
      _filePIDChildMisID.first =file2011;
      _filePIDChildMisID.second = file2012;
      _PIDChildMisID.first = histName;
      _PIDChildMisID.second= var;
    }
  else if ( key == "PIDChildProtonMisID") 
    {
      _filePIDChildProtonMisID.first =file2011;
      _filePIDChildProtonMisID.second = file2012;
      _PIDChildProtonMisID.first = histName;
      _PIDChildProtonMisID.second= var;
    }

}


TString MDFitterSettings::GetPIDFileName(TString key, TString year)
{
  if ( key == "PIDBachEff")
    {
      if ( year == "2011" ) { return _filePIDBacEff.first; }
      else {  return _filePIDBacEff.second; }
    }
  else if ( key == "PIDBachMisID")
    {
      if ( year == "2011") {return  _filePIDBacMisID.first; }
      else { return _filePIDBacMisID.second; }
    }
  else if ( key == "PIDChildKaonPionMisID" ) 
    {
      if ( year == "2011" ) { return _filePIDChildMisID.first; }
      else { return _filePIDChildMisID.second; }
    }
  else if ( key == "PIDChildProtonMisID")
    {
      if ( year == "2011" ) { return _filePIDChildProtonMisID.first; }
      else { return _filePIDChildProtonMisID.second; }
    }
  return ""; 
}


std::pair<TString,TString> MDFitterSettings::GetPIDHist(TString key)
{
  std::pair<TString,TString> n;
 
  if ( key == "PIDBachEff"){ return _PIDBacEff;}
  else if ( key == "PIDBachMisID"){ return _PIDBacMisID; }
  else if ( key == "PIDChildKaonPionMisID" ) { return _PIDChildMisID; }
  else if ( key == "PIDChildProtonMisID") { return  _PIDChildProtonMisID; }
  return n;

} 

TString MDFitterSettings::GetPIDHistName(TString key)
{
  if ( key == "PIDBachEff"){ return _PIDBacEff.first;}
  else if ( key == "PIDBachMisID"){ return _PIDBacMisID.first; }
  else if ( key == "PIDChildKaonPionMisID" ) { return _PIDChildMisID.first; }
  else if ( key == "PIDChildProtonMisID") { return  _PIDChildProtonMisID.first; }
  return "";
}

TString MDFitterSettings::GetPIDHistVar(TString key)
{
  if ( key == "PIDBachEff"){ return _PIDBacEff.second;}
  else if ( key == "PIDBachMisID"){ return _PIDBacMisID.second; }
  else if ( key == "PIDChildKaonPionMisID" ) { return _PIDChildMisID.second; }
  else if ( key == "PIDChildProtonMisID") { return  _PIDChildProtonMisID.second; }
  return "";
}

HistPID1D MDFitterSettings::GetHistPID1D(TString key, TString year)
{

  TString fileName = GetPIDFileName(key,year);
  TString fileName2 = GetPIDFileName(key,year); 
  if ( fileName == "#PID" ) { fileName2 = "#PID2"; } 
  if ( fileName == "#PID2m2" ) { fileName2 = "#PID2m22"; }
 
  TString histName = GetPIDHistName(key);

  if ( fileName == fileName2 )
    {
      std::cout<<"[INFO] Get histogram "<<histName<<" from file: "<<fileName<<std::endl; 
      std::cout<<_data<<std::endl; 
      HistPID1D hist(histName, histName, _data, fileName);
      return hist; 
    }
  else
    {
      std::cout<<"[INFO] Get histogram "<<histName<<" from files: "<<fileName<<" and "<<fileName2<<std::endl;
      std::cout<<_data<<std::endl;
      HistPID1D hist(histName, histName, _data, fileName, fileName2);
      return hist; 
    }
}



void MDFitterSettings::SetLabelDataMC(TString label, TString year)
{
  if ( year == "2011") { _ratioDMC.first = label; }
  else if ( year == "2012" ) { _ratioDMC.second = label; } 
  else
    {
      std::cout<<"[ERROR] Label for DataMC difference not set! Please check year: "<<year<<std::endl; 
    }
}

TString MDFitterSettings::GetLabelDataMC(TString year)
{
  TString l="";
  if ( year == "2011") { return _ratioDMC.first; }
  else if ( year == "2012" ) { return _ratioDMC.second; }
  else
    {
      std::cout<<"[ERROR] Label for DataMC difference not found! Please check year: "<<year<<std::endl;
    }
  return l; 
}


void MDFitterSettings::CorrectTagging()
{
  Int_t size1 = _useTag.size();
  Int_t size2 = this->GetNumTagVar();
  if ( size1 != size2 )
    {
     for(int i =0; i<size2; i++)
	{
	  _useTag[i] = _useTag[i+size2]; 
	}
    }
    
}

TString MDFitterSettings::CheckTagger(TString name)
{
  if (name.Contains("OS") ) { return "OS"; }
  else if (name.Contains("SSK")) { return "SSK";}
  else if (name.Contains("SSp")) { return "SSp";}
  else if (name.Contains("SS")) { return "SS";} 
  else { return "Unknown";} 
}


void MDFitterSettings::SetCalibration(TString match, Double_t p0, Double_t p1, Double_t av, Bool_t use)
{
  for ( int i = 0; i < this->GetNumTagVar(); i++ )
    {
      if ( _matchTag[i]  == match )
	{
	  _p0[i] = p0;
	  _p1[i] = p1; 
	  _av[i] = av;
	  _useTag[i] = use; 
	}
    }

  
}

Int_t MDFitterSettings::CheckNumUsedTag()
{
  Int_t num=0;
  for (int i = 0; i < _useTag.size(); i ++ )
    {
      if ( _useTag[i] == 1) { num++; }
    }
  return num; 
}

Double_t MDFitterSettings::GetCalibp0(TString match)
{
  Double_t val =0.0;
  for(int i = 0; i < this->GetNumTagVar(); i++)
    {
      if ( match == _matchTag[i] )
	{
          val = _p0[i]; 
	}
    }
  return val; 
}

Double_t MDFitterSettings::GetCalibp1(TString match)
{
  Double_t val =0.0;
  for(int i = 0; i < this->GetNumTagVar(); i++)
    {
      if ( match == _matchTag[i] )
	{
          val = _p1[i];
        }
    }
  return val;
}

Double_t MDFitterSettings::GetCalibAv(TString match)
{
  Double_t val =0.0;
  for(int i = 0; i < this->GetNumTagVar(); i++)
    {
      if ( match == _matchTag[i] )
	{
          val = _p0[i];
        }
    }
  return val;
}

std::vector <TString> MDFitterSettings::CheckTaggerList()
{
  std::vector <TString> tagList; 
  for(int i = 0; i < this->GetNumTagVar(); i++)
    {
      if ( _useTag[i] == true )
        {
          tagList.push_back(_matchTag[i]);
        }
    }
  return tagList; 

}
