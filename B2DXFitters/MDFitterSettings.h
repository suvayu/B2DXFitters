/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
 * Description: class contains settings for MDFitter                         *
 *                                                                           *
 * author: Agnieszka Dziurda  * agnieszka.dziurda@cern.ch                    *
 *                                                                           *
 *****************************************************************************/

#ifndef MDFITTERSETTINGS
#define MDFITTERSETTINGS

#include "TString.h"
#include "TNamed.h"
#include "TCut.h"
#include "RooRealVar.h"
#include "math.h"

#include <vector>
#include <fstream>
 
class MDFitterSettings : public TNamed {

public:
  MDFitterSettings(){};
  MDFitterSettings(const TString& name, const TString& title);
  MDFitterSettings(const TString& name, const TString& title, TString& file);
    
  MDFitterSettings(const MDFitterSettings& other);
  virtual TObject* clone() const { return new MDFitterSettings(*this); }

  virtual ~MDFitterSettings();

  friend std::ostream & operator<< (std::ostream &out, const MDFitterSettings &s);
  virtual void Print(Option_t * /*option*/ = "") const { std::cout<<*this<<std::endl;}

  std::vector <Double_t> GetMassBRange()    { return _massBRange;    }
  std::vector <Double_t> GetMassDRange()    { return _massDRange;    }
  std::vector <Double_t> GetMomRange()      { return _pRange;        }
  std::vector <Double_t> GetTrMomRange()    { return _ptRange;       }
  std::vector <Double_t> GetTracksRange()   { return _nTracksRange;  }
  std::vector <Double_t> GetBDTGRange()     { return _BDTGRange;     }
  std::vector <Double_t> GetPIDKRange()     { return _PIDRange;      }
  std::vector <Double_t> GetTimeRange()     { return _timeRange;     }
  std::vector <Double_t> GetTerrRange()     { return _terrRange;     }
  std::vector <Double_t> GetIDRange()       { return _idRange;       }
  std::vector <Double_t> GetTagRange(int i) 
    { std::vector <Double_t> range; 
      range.push_back(_tagVarRD[i]); 
      range.push_back(_tagVarRU[i]); 
      return range;
    }
  std::vector <Double_t> GetTagOmegaRange(int i) 
    { std::vector <Double_t> range; 
      range.push_back(_tagOmegaVarRD[i]); 
      range.push_back(_tagOmegaVarRU[i]); 
      return range;
    }

  Double_t GetMassBRangeDown()         { return _massBRange[0];    }
  Double_t GetMassDRangeDown()         { return _massDRange[0];    }
  Double_t GetMomRangeDown()           { return _pRange[0];        }
  Double_t GetTrMomRangeDown()         { return _ptRange[0];       }
  Double_t GetTracksRangeDown()        { return _nTracksRange[0];  }
  Double_t GetBDTGRangeDown()          { return _BDTGRange[0];     }
  Double_t GetPIDKRangeDown()          { return _PIDRange[0];      }
  Double_t GetTimeRangeDown()          { return _timeRange[0];     }
  Double_t GetTerrRangeDown()          { return _terrRange[0];     }
  Double_t GetIDRangeDown()            { return _idRange[0];       }
  Double_t GetTagRangeDown(int i)      { return _tagVarRD[i];      }
  Double_t GetTagOmegaRangeDown(int i) { return _tagOmegaVarRD[i];      }

  Double_t GetMassBRangeUp()         { return _massBRange[1];    }
  Double_t GetMassDRangeUp()         { return _massDRange[1];    }
  Double_t GetMomRangeUp()           { return _pRange[1];        }
  Double_t GetTrMomRangeUp()         { return _ptRange[1];       }
  Double_t GetTracksRangeUp()        { return _nTracksRange[1];  }
  Double_t GetBDTGRangeUp()          { return _BDTGRange[1];     }
  Double_t GetPIDKRangeUp()          { return _PIDRange[1];      }
  Double_t GetTimeRangeUp()          { return _timeRange[1];     }
  Double_t GetTerrRangeUp()          { return _terrRange[1];     }
  Double_t GetIDRangeUp()            { return _idRange[1];       }
  Double_t GetTagRangeUp(int i)      { return _tagVarRU[i]; }
  Double_t GetTagOmegaRangeUp(int i) { return _tagOmegaVarRU[i]; }

  Double_t GetRangeUp(TString var);
  Double_t GetRangeDown(TString var);
  std::vector <Double_t> GetRange(TString var);

  void SetMassBRange( std::vector <Double_t> range )    { _massBRange = range; }
  void SetMassDRange( std::vector <Double_t> range )    { _massDRange = range; }
  void SetTimeRange( std::vector <Double_t> range )     { _timeRange = range; }
  void SetMomRange( std::vector <Double_t> range )      { _pRange = range; }
  void SetTrMomRange( std::vector <Double_t> range )    { _ptRange = range; }
  void SetTracksRange( std::vector <Double_t> range )   { _nTracksRange = range; }
  void SetBDTGRange( std::vector <Double_t> range )     { _BDTGRange = range; }
  void SetPIDKRange( std::vector <Double_t> range )     { _PIDRange = range; }
  void SetTerrRange( std::vector <Double_t> range )     { _terrRange = range; }
  void SetIDRange( std::vector <Double_t> range )       { _idRange = range; }
  void SetTagRange( std::vector <Double_t> range, int i){ _tagVarRD[i] = range[0]; _tagVarRU[i] = range[1]; }
  void SetTagOmegaRange( std::vector <Double_t> range, int i){ _tagOmegaVarRD[i] = range[0]; _tagOmegaVarRD[i] = range[1]; }

  void SetMassBRange( Double_t range_down, Double_t range_up  )    { _massBRange[0] = range_down;     _massBRange[1] = range_up;    }
  void SetMassDRange( Double_t range_down, Double_t range_up  )    { _massDRange[0] = range_down;     _massDRange[1] = range_up;    }
  void SetTimeRange( Double_t range_down, Double_t range_up  )     { _timeRange[0] = range_down;      _timeRange[1] = range_up;     }
  void SetMomRange( Double_t range_down, Double_t range_up  )      { _pRange[0] = range_down;         _pRange[1] = range_up;        }
  void SetTrMomRange( Double_t range_down, Double_t range_up  )    { _ptRange[0] = range_down;        _ptRange[1] = range_up;       }
  void SetTracksRange( Double_t range_down, Double_t range_up  )   { _nTracksRange[0] = range_down;   _nTracksRange[1] = range_up;  }
  void SetBDTGRange( Double_t range_down, Double_t range_up  )     { _BDTGRange[0] = range_down;      _BDTGRange[1] = range_up;     }
  void SetPIDKRange( Double_t range_down, Double_t range_up  )     { _PIDRange[0] = range_down;       _PIDRange[1] = range_up;      }
  void SetTerrRange( Double_t range_down, Double_t range_up  )     { _terrRange[0] = range_down;      _terrRange[1] = range_up;     }
  void SetIDRange( Double_t range_down, Double_t range_up  )       { _idRange[0] = range_down;        _idRange[1] = range_up;       }
  void SetTagRange( Double_t range_down, Double_t range_up, int i ) { _tagVarRD[i] = range_down;      _tagVarRU[i] = range_up;      }
  void SetTagOmegaRange( Double_t range_down, Double_t range_up, int i ) { _tagOmegaVarRD[i] = range_down; _tagOmegaVarRU[i] = range_up; }

  TCut GetCut(TString var, bool sideband = false); 
  TCut GetCut(bool sideband = false);
  
  RooRealVar* GetObs(TString varName, bool log = false);

  std::vector <Int_t>   GetBin() { return _bin; }
  std::vector <TString> GetVar() { return _var; }
  
  Int_t   GetBin(Int_t i) { return _bin[i]; }
  TString GetVar(Int_t i) { return _var[i]; }

  void SetBin( std::vector <Int_t> bin ) { _bin = bin; }
  void SetVar( std::vector <TString> var ) { _var = var; }

  void SetBin(Int_t bin1, Int_t bin2, Int_t bin3 ) { _bin[0] = bin1; _bin[1] = bin2; _bin[3] = bin3; }
  void SetVar(Int_t var1, Int_t var2, Int_t var3 ) { _var[0] = var1; _var[1] = var2; _var[3] = var3; }

  Int_t GetPIDBach()   { return  _PIDBach;   }
  Int_t GetPIDChild()  { return  _PIDChild;  }
  Int_t GetPIDProton() { return  _PIDProton; }

  void SetPIDBach( Int_t value ) { _PIDBach = value; }
  void SetPIDChild( Int_t value ) { _PIDChild = value; }
  void SetPIDProton( Int_t value ) { _PIDProton = value; }

  std::vector <Double_t> GetLum() { return _lumRatio; }
  Double_t GetLum( Int_t i ) { return _lumRatio[i]; }
  Double_t GetLumRatio() { return _lumRatio[2]; }
  Double_t GetLumDown() { return _lumRatio[1]; }
  Double_t GetLumUp() { return _lumRatio[0]; }

  void SetLum( std::vector <Double_t> value ) { _lumRatio = value; }
  void SetLumDown( Double_t value ) { _lumRatio[1] = value; }
  void SetLumUp( Double_t value )   { _lumRatio[0] = value; }
  void SetLumRatio( Double_t value ) { _lumRatio[2] = value; }
  void SetLumRatio() { _lumRatio[2] = _lumRatio[0]/(_lumRatio[1]+_lumRatio[0]); }

  std::vector <TString>  GetCalibPion()   { return _calibPion; }
  std::vector <TString>  GetCalibKaon()   { return _calibKaon; }
  std::vector <TString>  GetCalibProton() { return _calibProton; }

  TString  GetCalibPionDown()   { return _calibPion[1]; }
  TString  GetCalibKaonDown()   { return _calibKaon[1]; }
  TString  GetCalibProtonDown() { return _calibProton[1]; }

  TString  GetCalibPionUp()   { return _calibPion[0]; }
  TString  GetCalibKaonUp()   { return _calibKaon[0]; }
  TString  GetCalibProtonUp() { return _calibProton[0]; }

  TString  GetCalibPionWorkName()   { return _calibPion[2]; }
  TString  GetCalibKaonWorkName()   { return _calibKaon[2]; }
  TString  GetCalibProtonWorkName() { return _calibProton[2]; }

  void SetCalibPion( std::vector <TString> calib ) { _calibPion = calib; }
  void SetCalibKaon( std::vector <TString> calib ) { _calibKaon = calib; }
  void SetCalibProton( std::vector <TString> calib ) { _calibProton = calib; }
  
  void SetCalibPion( TString calib_up, TString calib_down, TString workName ) { 
    _calibPion[0] = calib_up; _calibPion[1] = calib_down; _calibPion[2] = workName; 
  }
  void SetCalibKaon( TString calib_up, TString calib_down, TString workName ) {
    _calibKaon[0] = calib_up; _calibKaon[1] = calib_down; _calibKaon[2] = workName;
  }
  
  void SetCalibProton( TString calib_up, TString calib_down, TString workName ) {
    _calibProton[0] = calib_up; _calibProton[1] = calib_down; _calibProton[2] = workName;
  }

  TString GetMassBVar()    { return  _mVar;       }
  TString GetMassDVar()    { return _mDVar;       }
  TString GetTimeVar()     { return _tVar;        }
  TString GetTerrVar()     { return _terrVar;     } 
  TString GetIDVar()       { return _idVar;       }
  TString GetPIDKVar()     { return _PIDVar;      }
  TString GetBDTGVar()     { return _BDTGVar;     }
  TString GetTracksVar()   { return _nTracksVar;  }
  TString GetMomVar()      { return _pVar;        }
  TString GetTrMomVar()    { return _ptVar;       }
  TString GetTagVar(int i)  { return _tagVarNames[i]; }
  TString GetTagOmegaVar(int i) { return _tagOmegaVarNames[i]; }
  std::vector <TString> GetTagVar() { return _tagVarNames; }
  std::vector <TString> GetTagOmegaVar() { return _tagOmegaVarNames; }
  
  std::vector <TString> GetVarNames();

  void SetMassBVar(TString name)    { _mVar        = name; }
  void SetMassDVar(TString name)    { _mDVar       = name; }
  void SetTimeVar(TString name)     { _tVar        = name; }
  void SetTerrVar(TString name)     { _terrVar     = name; }
  void SetIDVar(TString name)       { _idVar       = name; }
  void SetPIDKVar(TString name)     { _PIDVar      = name; }
  void SetBDTGVar(TString name)     { _BDTGVar     = name; }
  void SetTracksVar(TString name)   { _nTracksVar  = name; }
  void SetMomVar(TString name)      { _pVar        = name; }
  void SetTrMomVar(TString name)    { _ptVar       = name; }
  void SetTagVar(TString name, int i) { _tagVarNames[i] = name; }
  void SetTagOmegaVar(TString name, int i) {_tagOmegaVarNames[i]= name; }
  void SetTagVar(std::vector <TString> name) {_tagVarNames = name; }
  void SetTagOmegaVar(std::vector <TString> name) {_tagOmegaVarNames = name;  }

  void SetNames( TString massB, TString massD, TString pidk, 
		 TString time, TString terr, TString BDTG, TString ID, TString p, TString pt, TString nTr)
  {
    _mVar = massB;
    _mDVar = massD;
    _tVar = time;
    _terrVar = terr ;
    _idVar = ID;
    _PIDVar = pidk;
    _BDTGVar = BDTG;
    _nTracksVar = nTr;
    _pVar = p;
    _ptVar = pt;
  } 
  
  Int_t GetWeightingDim() { return _weightDim; }
  void SetWeightingDim(Int_t dim) { _weightDim = dim; }

  Bool_t CheckAddVar() { return _addVar; }
  Int_t GetNumAddVar() { return _addVarNames.size(); }
  TString GetAddVarName(int i ) { return _addVarNames[i]; }
  Bool_t CheckVarName( TString name );
  
  void AddVar(TString name, Double_t dw, Double_t up ) { 
    _addVarNames.push_back(name); 
    _addVarRU.push_back(up); 
    _addVarRD.push_back(dw);
    if ( _addVar == false ) { _addVar = true; }
  }

  void RemoveAddVar(int i)
  {
    Int_t size = _addVarNames.size();
    if(size > 0 )
      {
	_addVarNames.erase(_addVarNames.begin()+i);
	_addVarRU.erase(_addVarRU.begin()+i);
	_addVarRD.erase(_addVarRD.begin()+i);
      }
    if(size == 1)
      {
	_addVar = false;
      }
  }

  void RemoveTagVar(int i)
  {
    Int_t size = _tagVarNames.size();
    if(size > 0 )
      {
        _tagVarNames.erase(_tagVarNames.begin()+i);
	_tagVarRU.erase(_tagVarRU.begin()+i);
        _tagVarRD.erase(_tagVarRD.begin()+i);
      }
    if(size == 1)
      {
	_tagVar = false;
      }
  }

  void RemoveTagOmegaVar(int i)
  {
    Int_t size = _tagOmegaVarNames.size();
    if(size > 0 )
      {
        _tagOmegaVarNames.erase(_tagOmegaVarNames.begin()+i);
        _tagOmegaVarRU.erase(_tagOmegaVarRU.begin()+i);
        _tagOmegaVarRD.erase(_tagOmegaVarRD.begin()+i);
      }
    if(size == 1)
      {
        _tagOmegaVar = false;
      }
  }

  
  Bool_t CheckTagVar() { return _tagVar; }
  Int_t GetNumTagVar() { return _tagVarNames.size(); }
  
  void AddTagVar(TString name, Double_t dw, Double_t up ) {
    _tagVarNames.push_back(name);
    _tagVarRU.push_back(up);
    _tagVarRD.push_back(dw);
    if ( _tagVar == false ) { _tagVar = true; }
  }

  Bool_t CheckTagOmegaVar() { return _tagOmegaVar; }
  Int_t GetNumTagOmegaVar() { return _tagOmegaVarNames.size(); }
  void AddTagOmegaVar(TString name, Double_t dw, Double_t up ) {
    _tagOmegaVarNames.push_back(name);
    _tagOmegaVarRU.push_back(up);
    _tagOmegaVarRD.push_back(dw);
    if ( _tagOmegaVar == false ) { _tagOmegaVar = true; }
  }
  
  void SetCalibp0(Int_t i, Double_t val){ _p0[i] = val;}
  void SetCalibp1(Int_t i, Double_t val){ _p1[i] = val;}
  void SetCalibAv(Int_t i, Double_t val){ _av[i] = val;}
  
  void SetCalibp0(std::vector <Double_t> val){ _p0 = val;}
  void SetCalibp1(std::vector <Double_t> val){ _p1 = val;}
  void SetCalibAv(std::vector <Double_t> val){ _av = val;}
  
  void SetCalibration(Int_t i, Double_t p0, Double_t p1, Double_t av) { _p0[i] = p0; _p1[i] = p1; _av[i] = av; }
  void AddCalibration(Double_t p0, Double_t p1, Double_t av) { _p0.push_back(p0); _p1.push_back(p1); _av.push_back(av); }
  
  Double_t GetCalibp0(Int_t i) { return _p0[i]; }
  Double_t GetCalibp1(Int_t i) { return _p1[i];}
  Double_t GetCalibAv(Int_t i) { return _av[i];}

  std::vector <Double_t> GetCalibp0() { return _p0; }
  std::vector <Double_t> GetCalibp1() {return _p1; }
  std::vector <Double_t> GetCalibAv() {return _av; }

  std::vector <Double_t> GetCalibration(Int_t i) { 
    std::vector <Double_t> vec;
    vec.push_back(_p0[i]);
    vec.push_back(_p1[i]);
    vec.push_back(_av[i]);
    return vec;
  }
  

protected:

  std::vector <Double_t> _massBRange;
  std::vector <Double_t> _massDRange;
  std::vector <Double_t> _timeRange;
  std::vector <Double_t> _terrRange;
  std::vector <Double_t> _pRange;
  std::vector <Double_t> _ptRange;
  std::vector <Double_t> _nTracksRange;
  std::vector <Double_t> _BDTGRange;
  std::vector <Double_t> _PIDRange;
  std::vector <Double_t> _idRange;

  TString _mVar;
  TString _mDVar;
  TString _tVar;
  TString _terrVar;
  TString _idVar;
  TString _PIDVar;
  TString _BDTGVar;
  TString _nTracksVar;
  TString _pVar;
  TString _ptVar;
  
  std::vector <Int_t> _bin;
  std::vector <TString> _var;

  Int_t _PIDBach;
  Int_t _PIDChild;
  Int_t _PIDProton;
  Int_t _weightDim;

  std::vector <Double_t> _lumRatio;

  std::vector <TString> _calibPion;
  std::vector <TString> _calibKaon;
  std::vector <TString> _calibProton;

  std::vector <TString> _addVarNames;
  std::vector <Double_t> _addVarRU;
  std::vector <Double_t> _addVarRD;
  Bool_t _addVar;

  std::vector <TString> _tagVarNames;
  std::vector <Double_t> _tagVarRU;
  std::vector <Double_t> _tagVarRD;
  Bool_t _tagVar;

  std::vector <TString>  _tagOmegaVarNames;
  std::vector <Double_t> _tagOmegaVarRU;
  std::vector <Double_t> _tagOmegaVarRD;
  Bool_t _tagOmegaVar;

  std::vector <Double_t> _p0;
  std::vector <Double_t> _p1;
  std::vector <Double_t> _av;

private:
  ClassDef(MDFitterSettings, 1);
};
 
#endif
