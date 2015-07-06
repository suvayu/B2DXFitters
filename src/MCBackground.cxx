/*****************************************************************************                                                                                                                
 * Project: RooFit                                                           *                                                                                                                
 *                                                                           *                                                                                                              
 * Description: class contains MC background properties                      *                                                                                                             
 *                                                                           *                                                                                                                
 * author: Agnieszka Dziurda  * agnieszka.dziurda@cern.ch                    *                                                                                                               
 *                                                                           *                                                                                                                
 *****************************************************************************/


#include "Riostream.h"

#include "B2DXFitters/MCBackground.h"
#include "B2DXFitters/GeneralUtils.h"
#include "TString.h"
#include "RooRealVar.h"
#include "RooArgSet.h"
#include "TNamed.h"
#include "TCut.h"
#include "TMath.h"
#include "TFile.h"
#include "TTree.h"

#include <vector>
#include <fstream>

using namespace GeneralUtils;

MCBackground::MCBackground(const TString& name, const TString& title)
{
  TNamed(name,title);

  _mode = "";
  _fileName = "";
  _treeName = "";
  _tree = NULL;
  _rho = 1.0;
  _opt = "";
  _pol = ""; 
  _file = NULL; 
}

MCBackground::MCBackground(const TString& name, const TString& title, TString& nameFile, TString& sig, Int_t num)
{
  TNamed(name,title);
  _mode = "";
  _fileName = "";
  _treeName = "";
  _rho = 1.5;
  _opt = "Both";
  _pol = CheckPolarity(sig,false);
  _year = CheckDataYear(sig,false); 

  std::ifstream myfile(nameFile.Data());
  std::string line, line1;
  size_t l1;
  if (myfile.is_open())
    {
      while(myfile.good())
        {
          getline (myfile,line); 
	  if ( line == sig.Data() )
	    {

	      for( int i = 0; i<num; i++ )
		{
		  getline(myfile, line, '}');
		  if (line == "###") { break; } 
		}

	      line.erase(std::remove(line.begin(), line.end(), ' '),line.end());
	      if ( line.find("Mode") != std::string::npos )
		{
		  line1 = line;
		  l1 = line1.find("Mode");
		  line1 = line1.substr(l1+7,line1.size());
		  l1 = line1.find(",");
		  if ( l1 > line1.size() )
		    {
		      l1 = line1.find("}"); 
		    }
		  line1 = line1.substr(0,l1);
		  l1 = line1.find("\"");
		  line1 = line1.substr(0,l1);
		  _mode = line1;

		}
	      if ( line.find("FileName") != std::string::npos )
		{
		  line1 = line;
		  l1 = line1.find("FileName");
                  line1 = line1.substr(l1+11,line1.size());
                  l1 = line1.find(",");
                  if ( l1 > line1.size() )
                    {
		      l1 = line1.find("}");
                    }
                  line1 = line1.substr(0,l1);
		  l1 = line1.find("\"");
                  line1 = line1.substr(0,l1);
		  _fileName = line1;

		}
	      if ( line.find("TreeName") != std::string::npos )
		{
		  line1 = line;
		  l1 = line1.find("TreeName");
                  line1 = line1.substr(l1+11,line1.size());
                  l1 = line1.find(",");
                  if ( l1 > line1.size() )
                    {
		      l1 = line1.find("}");
                    }
                  line1 = line1.substr(0,l1);
		  l1 = line1.find("\"");
                  line1 = line1.substr(0,l1);
		  _treeName = line1; 
		}
	      if ( line.find("Smooth") != std::string::npos )
		{
		  line1 = line;
		  l1 = line1.find("Smooth");
                  line1 = line1.substr(l1+8,line1.size());
                  l1 = line1.find(",");
                  if ( l1 > line1.size() )
                    {
                      l1 = line1.find("}");
                    }
                  line1 = line1.substr(0,l1);
		  _rho = (Double_t)atof(line1.c_str());

		}
	      if ( line.find("Mirror") != std::string::npos )
		{
		  line1 = line;
                  l1 = line1.find("Mirror");
                  line1 = line1.substr(l1+9,line1.size());
                  l1 = line1.find(",");
                  if ( l1 > line1.size() )
                    {
                      l1 = line1.find("}");
                    }
                  line1 = line1.substr(0,l1);
                  l1 = line1.find("\"");
                  line1 = line1.substr(0,l1);
                  _opt = line1;
		}
	    }
	}
    }
  myfile.close(); 
  this->CheckMode(); 

  _file = NULL;
  _tree = NULL; 
  _file = TFile::Open(_fileName.Data());
  _tree = (TTree*) _file->Get(_treeName.Data());

}

MCBackground::MCBackground(const MCBackground& other):TNamed(other) 
{
  _mode   = other._mode;
  _fileName = other._fileName;
  _treeName = other._treeName;
  _tree = other._tree;
  _file = other._file; 
  _rho = other._rho;
  _opt = other._opt; 
  _pol = other._pol;
  _year = other._year;
}

MCBackground::~MCBackground() { }

std::ostream & operator<< (std::ostream &out, const MCBackground &s)
{
  out<<"MCBackground for mode: "<<s._mode<<std::endl;
  out<<"FileName: "<<s._fileName<<std::endl;
  out<<"TreeName: "<<s._treeName<<std::endl;
  out<<"Polarity, year: "<<s._pol<<","<<s._year<<std::endl; 
  out<<"RooKeysPdf options (rho,mirrors):("<<s._rho<<","<<s._opt<<")"<<std::endl;
  return out; 
}


TString MCBackground::CheckMode()
{
  TString modeOut;
  TString Bs = "";
  TString Ds = "";
  TString Bach = "";

  if ( _mode.Contains("Combinatorial") == true ) { return _mode; } 
  if ( _mode.Contains("Lb") == true ||
       _mode.Contains("lambdab") == true  ||
       _mode.Contains("Lambdab") == true ){ Bs="Lb";}
  else if( _mode.Contains("Bs")  == true  || _mode.Contains("bs") == true) { Bs = "Bs"; }
  else if (( _mode.Contains("Bd") == true || _mode.Contains("bd") == true ) && _mode.Contains("ambda") == false )
    { Bs="Bd"; }
  else { Bs="Comb";}

  if (_mode.Contains("Lc") == true ||
      _mode.Contains("lambdac") == true ||
      _mode.Contains("Lambdac") == true) { Ds = "Lc";}
  else if (_mode.Contains("Dsst") == true || _mode.Contains("dsst") == true)
    { Ds ="Dsst";}
  else if ( (_mode.Contains("Ds") == true  || _mode.Contains("ds")== true) &&
	    (_mode.Contains("Dsst") == false || _mode.Contains("dsst") == false ))
    { Ds = "Ds";}
  else if (( _mode.Contains("D") == true  || _mode.Contains("d") == true )  &&
	   (_mode.Contains("Ds") == false  || _mode.Contains("ds") == false) && _mode.Contains("ambda") == false)
    {Ds = "D";}
  else { Ds ="bkg";}

  if ( _mode.Contains("KPi0") == true || _mode.Contains("Kpi0") == true || _mode.Contains("kpi0") == true || _mode.Contains("kPi0") == true ) { Bach = "KPi0"; } 
  else if ( _mode.Contains("Pi") == true || _mode.Contains("pi") == true) { Bach = "Pi"; }
  else if( ( _mode.Contains("P") == true || _mode.Contains("p") == true ) &&
	   ( _mode.Contains("Pi") == false || _mode.Contains("pi") == false))
    {Bach = "p";}
  else if( _mode.Contains("Kst") == true || _mode.Contains("kst") == true ) {Bach ="Kst";}
  else if( _mode.Contains("Rho") == true || _mode.Contains("rho") == true ) {Bach = "Rho";}
  else if( (_mode.Contains("K") == true || _mode.Contains("k") == true )&&
	   (_mode.Contains("Kst") == false || _mode.Contains("kst") == false) )
    {Bach = "K";}
  else { Bach ="";}

  modeOut = Bs+"2"+Ds+Bach;
 
  if ( modeOut != _mode )
    {
      std::cout<<"[INFO] Changed mode label from: "<< _mode <<" to: "<<modeOut<<std::endl;
      _mode = modeOut; 
    }
  
  return _mode;
}
