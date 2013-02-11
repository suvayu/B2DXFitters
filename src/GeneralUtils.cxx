//---------------------------------------------------------------------------//
//                                                                           //
//  General utilities                                                        //
//                                                                           //
//  Source file                                                              //
//                                                                           //
//  Authors: Agnieszka Dziurda, Eduardo Rodrigues                            //
//  Date   : 12 / 04 / 2012                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

// STL includes
#include <string>
#include <vector>
#include <fstream>
#include <stdexcept>

// ROOT and RooFit includes
#include "TH1D.h"
#include "TProfile.h"
#include "TFile.h"
#include "TCanvas.h"
#include "TLorentzVector.h"
#include "RooFormulaVar.h"
#include "RooAddPdf.h"
#include "RooExtendPdf.h"
#include "RooEffProd.h"
#include "RooGaussian.h"
#include "RooDecay.h"
#include "RooBDecay.h"
#include "RooCBShape.h"
#include "RooArgSet.h"
#include "RooPlot.h"
#include "RooNLLVar.h"
#include "RooMinuit.h"
#include "RooFitResult.h"
#include "TH2F.h"
#include "TRandom3.h"
#include "RooHistPdf.h"
#include "RooDataHist.h"
#include "RooCategory.h"
// B2DXFitters includes
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/KinHack.h"
#include "B2DXFitters/DecayTreeTupleSucksFitter.h"

#define DEBUG(COUNT, MSG)				   \
  std::cout << "SA-DEBUG: [" << COUNT << "] (" << __func__ << ") " \
  << MSG << std::endl; \
  COUNT++;

#define ERROR(COUNT, MSG) \
  std::cerr << "SA-ERROR: [" << COUNT << "] (" << __func__ << ") " \
  << MSG << std::endl; \
  COUNT++;

namespace GeneralUtils {

  //===========================================================================
  // Save the data and corresponding template PDF, if given, on a file
  // Note: data/PDF need to depend on the observable, obviously ;-)!
  // "extension" is the file extension. Typically: root, png, pdf, eps
  // "mode" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "suffix" can be used e.g. to separed magnet up from down plots
  //===========================================================================
  void saveDataTemplateToFile( RooAbsData* data,
                               RooAbsPdf*  pdf,
                               RooRealVar* observable,
                               const char* mode,
                               const char* extension,
                               const char* suffix,
                               bool        debug
                               )
  {
    if ( debug )
      printf( "==> GeneralUtils::saveDataTemplateToFile( data=%s, pdf=%s, obs=%s, mode=%s, ext=%s, suffix=%s, debug=%s )\n",
              data -> GetName(), pdf ? pdf -> GetName() : "NULL",
              observable -> GetName(),
              mode, extension, suffix, debug ? "true" : "false" );
    
    // Just checking for NULL pointers ;-)
    if ( ! data )
    {
      printf( "[ERROR] The input RooAbsData is NULL ! Nothing done.\n" );
      exit( -1 );
    }
    
    char identifier[100];
    sprintf( identifier, "%s%s%s", mode,
             ( suffix == NULL ? "" : "_" ),
             ( suffix == NULL ? "" : suffix )
             );
    
    const char* name = Form( "canvas_%s", identifier );
    TCanvas* canvas = new TCanvas( name, name );
    canvas -> cd();
    
    RooPlot* frame = observable -> frame();
    frame -> SetName( Form( "frame_%s", identifier ) );
    
    data  -> plotOn( frame, RooFit::MarkerColor(kRed), RooFit::Binning(50) );
    if ( pdf ) pdf -> plotOn( frame, RooFit::LineColor(kRed) );
    frame -> Draw();
    
    name = Form( "Plot/data_%s.%s", identifier, extension );
    if ( pdf ) name = Form( "Plot/template_%s.%s", identifier, extension );
    canvas -> Print( name );
    printf( "[INFO] \"%s\" file saved.\n", name );
  }
  
  //===========================================================================
  // Read PID histogram,
  // FilePID - collect path and file names to the mu and md root files
  // nameHist - is the name of histogram which should be read
  // sample - determines from which root file histogram should be read   
  //===========================================================================

  TH1F* ReadPIDHist( std::vector <std::string> &FilePID,
                     TString &nameHist,
                     int sample,
		     bool debug
                     )
  {
    if ( debug == true) 
      {
	std::cout<<"[INFO] ==> GeneralUtils::ReadPIDHist(...)"<<std::endl;
      }
    std::string name;
    int i=sample;
    TH1F* hist = NULL;
    TFile* file = NULL;
    name = FilePID[0]+FilePID[i+1];
    file = TFile::Open(name.c_str());
    hist = (TH1F*)file->Get(nameHist.Data());
    if( hist != NULL )
      { 
	if ( debug == true) std::cout<<"Took histogram: "<<hist->GetName()<<std::endl;
	return hist;
      }
    else
      { 
	if ( debug == true) std::cout<<"Cannot take a histogram"<<std::endl; 
	return NULL;
      }
  }

  //===========================================================================
  // Add PID histogram with weights,
  // hist1 - first histogram;
  // w1 - weight 1
  // hist2 - first histogram;
  // w2 - weight 1
  //===========================================================================


  TH1F*AddHist(TH1F* hist1, Double_t w1, TH1F* hist2, Double_t w2, bool debug )
  {
    
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::AddHist(...)"<<std::endl;
    Double_t w = w1+w2;
    
    Int_t bin1 = hist1->GetNbinsX();
    Double_t min1 = hist1->GetXaxis()->GetXmin();
    Double_t max1 = hist1->GetXaxis()->GetXmax();
    
    Double_t min2 = hist2->GetXaxis()->GetXmin();
    Double_t max2 = hist2->GetXaxis()->GetXmax();

    Double_t bin;
    Double_t min;
    Double_t max;
    
    bin = bin1;
    if ( min1 > min2 ) { min=min2; } else { min=min1; }
    if ( max1 > max2 ) { max=max1; } else { max=max2; }

    //std::cout<<"hist1: bin: "<<bin1<<" in range=("<<min1<<","<<max1<<")"<<std::endl;
    //std::cout<<"hist2: bin: "<<bin2<<" in range=("<<min2<<","<<max2<<")"<<std::endl;
    //std::cout<<"hist0: bin: "<<bin<<" in range=("<<min<<","<<max<<")"<<std::endl;

    hist1->SetBins(bin,min,max);
    hist2->SetBins(bin,min,max);
    
    TH1F* hist = new TH1F(hist1->GetName(),hist1->GetTitle(),bin,min,max);
    
    for(int i=0; i<bin; i++)
      {
	Double_t bin1 = hist1->GetBinContent(i);
	Double_t bin2 = hist2->GetBinContent(i);
	Double_t bin = (bin1*w1+bin2*w2)/w;
	//std::cout<<"i: "<<i<<" bin1: "<<bin1<<" bin2: "<<bin2<<" bin: "<<bin<<std::endl;
	hist->SetBinContent(i,bin);
      }
    return hist;
    
  }

  //===========================================================================
  // Read one name from config.txt file 
  // filesDir - path to the file
  // FileName - output 
  // sig - signature which should be read from file, for example sig="#DsPi"
  // to FileName will be read everything what is between sig and "###" 
  //===========================================================================
  
  void ReadOneName(TString& filesDir,
		   std::vector <std::string> &FileName, 
		   TString& sig, bool debug)
  {
    std::string line;
    std::ifstream myfile(filesDir.Data());

    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::ReadOneName(...). Read names from file"<<std::endl;

    if (myfile.is_open())
      {
        while(myfile.good())
          {
            getline (myfile,line);

            if(line == sig.Data() ){
              while( line != "###" ){
                getline (myfile,line);
                if( line != "###"){ FileName.push_back(line.c_str());}
              }
            }
	  }
      }
    else { if ( debug == true) std::cout<<"Unable to open a file"<<std::endl;}

  }

  //===========================================================================
  // Read tree from TFile. The convention which should be in the .txt file:
  // line 1: path to directory for example: /afs/cern.ch/work/g/gligorov/public/Bs2DsKFitTuples/
  // line 2: name of the first file, for example: FitTuple_MergedTree_Bd2DPi_D2KPiPi_MD_BDTG_MINI.root
  // line 3: name of the second file, for example: FitTuple_MergedTree_Bd2DPi_D2KPiPi_MU_BDTG_MINI.root
  // line 4: name of tree for the first file, for example: DecayTree
  // line 5: name of tree for the second file, for example: DecayTree  
  //===========================================================================

  TTree* ReadTreeData(std::vector <std::string> &FileName,int  sample, bool debug)
  {
  
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::ReadTreeData(...). Read TTree from FileName"<<std::endl;

    int i=sample;
    std::string name[5];

    TFile* file = NULL;
    TTree* tree = NULL;
    
    name[0] = FileName[0]+FileName[i+1];
    file = TFile::Open(name[0].c_str());
    tree = (TTree*) file->Get(FileName[i+3].c_str());
    if  ( tree ==  NULL ) {
      std::cout<<" Cannot open file: "<<FileName[0]+FileName[i+1]<<std::endl;
      return NULL;
    }
    else {  
      if ( debug == true)
	{
	  std::cout<<"Open file: "<<FileName[0]+FileName[i+1]<<std::endl;
	  std::cout<<"with Tree: "<<tree->GetName()<<std::endl;
	  std::cout<<"----------------------------------------------------------"<<std::endl;
	}
      return tree;
    }
    
  }

  //===========================================================================
  // Read tree from TFile. 
  // fileName - path to the TFile
  // treeName - name of the TTree 
  //===========================================================================
    
  TTree* ReadTreeMC(const char* fileName, const char* treeName, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::ReadTreeMC(...). Read Tree from MC"<<std::endl;

    TFile* file = NULL;
    TTree* tree = NULL;
    file = TFile::Open(fileName);
    tree = (TTree*) file->Get(treeName);

    if ( tree != NULL ){ 
      if ( debug == true)
	{
	  std::cout<<": Open MC File: "<<fileName<<std::endl; std::cout<<"with tree: "<<treeName<<std::endl;
	  std::cout<<"Number of events: "<<tree->GetEntries()<<std::endl; 
	  std::cout<<"----------------------------------------------------------"<<std::endl;
	}
      return tree;
    }
    else { if ( debug == true) std::cout<<"Cannot open MCFile"<<std::endl; return NULL;}
  }

  //===========================================================================
  // Read one name (mode) for MC2011-March  
  // if the path to the MC file: /afs/cern.ch/project/lbcern/vol0/adudziak/MCAddBDTG/Merged_Bd2DstPi_Dst2D-Pi0_MD_BsHypo_BDTG.root then
  // 1. find last / and cut only file name
  // 2. cut between first "_" and second "_", here: Bd2DstPi
  //===========================================================================

  TString ReadOneMode( TString path, bool debug )
 {
   if ( debug == true) std::cout<<"[INFO] GeneralUtils::ReadOneMode(...)"<<std::endl;

    TString mode;
    TString tmps;
    char c[]={"/"};
    

    Ssiz_t max;
    Ssiz_t p=0;
    max=path.Last(c[0]);
    
    if( std::string::size_type(max) != std::string::npos) {
	tmps = path.Remove(p,max+1);
    } else {
	tmps = path;
    }

    max = tmps.First("_");     
    TString t = tmps.Remove(p,max+1);
    Ssiz_t end = t.First("_");
    Ssiz_t endend = t.Length();
    mode = t.Replace(end,endend,"");
    return mode;
 }

  //===========================================================================
  // Read all modes for MC2011-March
  // MCFileName - collects all paths to the MC files
  // mode - output 
  // Please not that we dont have MC Bd2DsstPi and Bs2DsstKst and they are
  // loaded from Bs2DsstPi and Bd2DKst, respectively. But the mode is change 
  // only if Bs2DsstPi ( or Bd2DKst ) are used twice in MCFileName
  //==========================================================================

  void ReadMode(std::vector <std::string> &MCFileName, 
		std::vector <std::string> &mode, bool iskfactor, bool debug)
  {
    
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::ReadMode(...). Read MC modes for backgrounds"<<std::endl;

    std::vector <std::string> tmps;
    std::string s="/";

    for( unsigned i =0; i<MCFileName.size(); i++){
      size_t max, max1;
      size_t p=0;
      max=MCFileName[i].find_last_of("/");
      if( max != std::string::npos){ tmps.push_back(MCFileName[i].substr(max+1)); }
      else{ tmps.push_back(MCFileName[i]);}
      max = tmps[i].find("_");
      max1 = tmps[i].find("Merged_");
      if( max1 == 0) {
	std::string t = tmps[i].substr(max+1);
        size_t end = t.find("_");
        mode.push_back(t.substr(p,end));
      }
      else {
	if( max != std::string::npos){

	  std::string t = tmps[i].substr(p,max);
	  mode.push_back(t); }
      }
    }

    unsigned kst_count(0), DsstPi_count(0), DsstK_count(0), DsRho_count(0);

    for( unsigned i = 0; i < MCFileName.size(); i++)
      {
	if (mode[i] == "Bs2DsstK") {
	  if (DsstK_count == 1) mode[i] = "Bd2DsstK";
	  DsstK_count++;
	  continue;
	}

	if (mode[i] == "Bd2DKst") {
	  if(kst_count == 0 and not iskfactor) mode[i]="Bs2DsKst";
	  if(kst_count == 1) mode[i]="Bs2DsstKst";
	  if(kst_count == 2) mode[i]="Bd2DsKst";
	  kst_count++;
	  continue;
	}

	if(mode[i] == "Bs2DsstPi") {
	  if (DsstPi_count == 1) mode[i]="Bd2DsstPi";
	  DsstPi_count++;
	  continue;
	}

	if (mode[i] == "Bs2DsRho") {
	  if (DsRho_count == 1) mode[i] = "Bs2DsKst";
	  DsRho_count++;
	}
      }

    if ( debug == true)
      {
	std::cout<<"Modes: "<<std::endl;
	for( unsigned i = 0; i < MCFileName.size(); i++)
	  {
	    std::cout<<mode[i]<<std::endl;
	  }
      }
  }

  //===========================================================================
  // Save template to the pdf file
  //==========================================================================

  void SaveTemplate(RooDataSet* dataSet, 
		    RooKeysPdf* pdf, 
		    RooRealVar* mass, 
		    TString &sample, 
		    TString &mode, bool debug )
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::SaveTemplate(...). Saving template for background to pdf file"<<std::endl;

    TCanvas*  can=NULL;
    RooPlot* frame=NULL;
    TString name,name2,name3;
    name3 ="_"+sample;
    name2 =mode+name3;
    name="canvas_"+name2;
    can = new TCanvas(name.Data(),name.Data());
    can->cd();
    frame = (RooPlot*)mass->frame();
    name="frame_"+name2;
    frame->SetName(name.Data());
                                                                                                         
    dataSet->plotOn(frame, RooFit::MarkerColor(kRed), RooFit::Binning(50));
    pdf->plotOn(frame, RooFit::LineColor(kRed));
    frame->Draw();

    TString name1;
    name1="Plot/template_"+name2;
    name=name1+".pdf";

    can->Print(name.Data());

  }

  //===========================================================================
  // Save histogram template to the pdf file
  //==========================================================================

  void SaveTemplateHist(RooDataHist* dataSet,
			RooHistPdf* pdf,
			RooRealVar* mass,
			TString &sample,
			TString &mode, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::SaveTemplateHist(...). Saving template for background to pdf file"<<std::endl;

    TCanvas*  can=NULL;
    RooPlot* frame=NULL;
    TString name,name2,name3;
    name3 ="_"+sample;
    name2 =mode+name3;
    name="canvas_"+name2;
    can = new TCanvas(name.Data(),name.Data());
    can->cd();
    frame = (RooPlot*)mass->frame();
    name="frame_"+name2;
    frame->SetName(name.Data());
    
    dataSet->plotOn(frame, RooFit::MarkerColor(kRed));
    pdf->plotOn(frame, RooFit::LineColor(kRed));
    frame->Draw();

    TString name1;
    name1="Plot/template_"+name2;
    name=name1+".pdf";

    can->Print(name.Data());
  
  }


  //===========================================================================
  // Save projection of data set  to the pdf file
  // Sample and mode are used to create name
  //==========================================================================

  void SaveDataSet(RooDataSet* dataSet, 
		   RooRealVar* mass,
		   TString &sample,
		   TString &mode, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::SaveDataSet(...). Saving plot data set to pdf file"<<std::endl;

    TCanvas*  can=NULL;
    RooPlot* frame=NULL;
    TString name,name2,name3;
    name3 ="_"+sample;
    name2 =mode+name3;
    name="canvas_data_"+name2;
    can = new TCanvas(name.Data(),name.Data());
    can->cd();
    frame = (RooPlot*)mass->frame();
    name="frame_data_"+name2;
    frame->SetName(name.Data());
    
    dataSet->plotOn(frame, RooFit::MarkerColor(kRed), RooFit::Binning(50),RooFit::DataError(RooAbsData::SumW2));
    frame->Draw();

    TString name1;
    name1="Plot/dataset_"+name2;
    name=name1+".pdf";

    can->Print(name.Data());
  }

  //===========================================================================
  // Obtain new tree from the old tree using TCut cut 
  // Sample and mode are used to create name
  //==========================================================================
  
  TTree* TreeCut(TTree* tree, 
		 TCut &cut, 
		 TString &sample, 
		 TString &mode, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils.TreeCut(...)"<<std::endl;

    TFile* tfiletmp = NULL;
    TTree* treetmp = NULL;
    TString  name, name2, name3;
    name3 ="_"+sample;
    name2 =mode+name3;
    name="Cut_tree_"+name2;
    treetmp = new TTree(name.Data(),name.Data());
    name = "Trash/Cut_file_"+name2+".root";
    tfiletmp = new TFile(name.Data(),"recreate");
    treetmp->SetDirectory(tfiletmp);
    treetmp = tree->CopyTree(cut);
    if( treetmp != NULL ){ 
      Double_t eff = (Double_t)treetmp->GetEntries()/tree->GetEntries()*100;
      if ( debug == true) std::cout<<mode<<" Old tree: "<< tree->GetEntries() <<" New tree: "<<treetmp->GetEntries()<<" eff: "<<eff<<"%"<<std::endl;
      return treetmp;
    }
    else { if ( debug == true) std::cout<<" Cannot cut tree "<<std::endl; return NULL; }
  }

  //===========================================================================
  // Create RooKeysPdf for dataSetMC with observable massMC. 
  // Sample and mode are used to create the name of RooKeysPdf.   
  //==========================================================================

  RooKeysPdf* CreatePDFMC(RooDataSet* dataSetMC,
			  RooRealVar* massMC, 
			  TString &sample,
			  TString &mode, Bool_t mistag, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::CreatePDFMC(...). Create RooKeysPdf for MC"<<std::endl;

    RooKeysPdf* pdfMC = NULL;
    TString name3, name2, name;
    name3="Pdf_m_"+sample;
    name2= mode+name3;
    name="PhysBkg"+name2;
    if (mode.Contains("Lb") || mistag == true )
      {
	pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorBoth,1.5);
      }
    else 
      {
	pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorBoth,3.0);
      }
//    else
//      {
//	pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorBoth,3.0);
//      }
    if( pdfMC != NULL ) { if ( debug == true) std::cout<<"Create RooKeysPdf for PartRec: "<<pdfMC->GetName()<<std::endl; return pdfMC; }
    else { if ( debug == true) std::cout<<"Cannot create pdf"<<std::endl; return NULL;}
    
  }

  //===========================================================================
  // Get observable ( obs ) from workspace (work)
  //==========================================================================

  RooRealVar* GetObservable(RooWorkspace* work, 
			    TString &obs, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::GetObservable("<<work->GetName()<<","<<obs<<")"<<std::endl;

    RooRealVar* obser = NULL;
    obser = (RooRealVar*)work->var(obs.Data());
    if( obser != NULL ){ if ( debug == true) std::cout<<"Read observable: "<<obser->GetName()<<std::endl; return obser; }
    else{ if ( debug == true) std::cout<<"Cannot read observable"<<std::endl; return NULL;}
  }

  //===========================================================================
  // Get data set ( dat ) from workspace (work)
  //==========================================================================

  RooDataSet* GetDataSet(RooWorkspace* work, 
                         TString &dat, bool debug )
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::GetDataSet("<<work->GetName()<<","<<dat<<")"<<std::endl;

    RooDataSet* data = NULL;
    data = (RooDataSet*)work->data(dat.Data());
    if( data != NULL ){ 
      if ( debug == true) std::cout<<"Read data set: "<<data->GetName()<<" with number of entries: "<<data->numEntries()<<std::endl; 
      return data; 
    }
    else{ if ( debug == true) std::cout<<"Cannot read data set"<<std::endl; return NULL;}

  }

  //===========================================================================
  // Get data histogram ( dat ) from workspace (work)
  //==========================================================================

  RooDataHist* GetDataHist(RooWorkspace* work,
			   TString &dat, 
			   bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::GetDataSet("<<work->GetName()<<","<<dat<<")"<<std::endl;

    RooDataHist* data = NULL;
    data = (RooDataHist*)work->data(dat.Data());
    if( data != NULL ){
      if ( debug == true) std::cout<<"Read data set: "<<data->GetName()<<" with number of entries: "<<data->numEntries()<<std::endl;
      return data;
    }
    else{ if ( debug == true) std::cout<<"Cannot read data set"<<std::endl; return NULL;}

  }


  //===========================================================================
  // Save workspace in the ROOT file 
  //==========================================================================
  
  void SaveWorkspace(RooWorkspace* work, 
		     TString &name, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] => GeneralUtils::SaveWorkspace("<<work->GetName()<<","<<name<<")"<<std::endl;

    Bool_t err =work->writeToFile(name.Data());
    if (err == false){ if ( debug == true) std::cout<<"Workspace saved sucessfully to file: "<<name<<std::endl;}
    else { if ( debug == true) std::cout<<"Workspace save failed"<<std::endl;}
  }

  //===========================================================================
  // Load workspace from the ROOT file
  //==========================================================================

  RooWorkspace* LoadWorkspace(TString &filename, 
			      TString& workname, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] => GeneralUtils.LoadWorkspace("<<filename<<","<<workname<<")"<<std::endl;
  
    TFile* file = NULL;
    RooWorkspace* work = NULL;
    file = TFile::Open( filename.Data() );
    if(file != NULL ){ if ( debug == true) std::cout<<"Open file: "<<file->GetName()<<std::endl;} else {std::cout<<"Cannot open file"<<std::endl; return NULL;}
    work = (RooWorkspace*) file -> Get( workname.Data() ); 
    if( work != NULL ){
      if ( debug == true) std::cout<<"Read workspace: "<<work->GetName()<<std::endl;
      work->Print();
      return work;
     }
    else{ if ( debug == true) std::cout<<"Cannot read workspace"<<std::endl; return NULL;}

  }

  //===========================================================================
  // Check polarity (down,up) from check
  //==========================================================================

  TString CheckPolarity(std::string& check, bool debug)
  {
    TString polarity;
    if (check.find("MD") != std::string::npos  || check.find("down") != std::string::npos || check.find("dw") != std::string::npos ||\
	check.find("Down") != std::string::npos || check.find("md") != std::string::npos)
      { 
	polarity = "down"; 
      }
    else if ( check.find("MU") != std::string::npos || check.find("up") != std::string::npos || check.find("Up") != std::string::npos\
	      || check.find("mu") != std::string::npos )
      { 
	polarity = "up"; 
      }
    else 
      { 
	polarity = ""; 
      }
    if ( debug == true) std::cout<<"[INFO] Sample: "<<polarity<<std::endl;
    return polarity;
  }  
  
  //===========================================================================
  // Check D/Ds final state (kkpi,kpipi,pipipi) from check
  //==========================================================================
  TString CheckDMode(std::string& check, bool debug)
  {
    TString dmode;
    if (check.find("KKpi") != std::string::npos  || check.find("KKPi") != std::string::npos || check.find("kkpi") != std::string::npos )
      {
        dmode = "kkpi";
      }
    else if ( check.find("Kpipi") != std::string::npos || check.find("KPiPi") != std::string::npos || check.find("kpipi") != std::string::npos)
      {
        dmode = "kpipi";
      }
    else if ( check.find("pipipi") != std::string::npos || check.find("PiPiPi") != std::string::npos )
      {
        dmode = "pipipi";
      }
    else 
      {
        dmode = "";
      }
    if ( debug == true) std::cout<<"[INFO] Sample: "<<dmode<<std::endl;
    return dmode;
  }
 


} //end of namespace
