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
#include <cmath>

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
#include "RooCategory.h"
#include "TH1.h"
#include "TH2F.h"
#include "TH3F.h"
#include "TRandom3.h"
#include "RooHistPdf.h"
#include "RooDataHist.h"
#include "RooCategory.h"
#include "TStyle.h"
#include "TLatex.h"
#include "RooBinning.h"
#include "RooAbsBinning.h"
#include "RooAbsRealLValue.h"
#include "RooArgList.h"
#include "RooConstVar.h"
 
// B2DXFitters includes
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/KinHack.h"
#include "B2DXFitters/DecayTreeTupleSucksFitter.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"
#include "B2DXFitters/PlotSettings.h"

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
			       const char* dir,
			       Int_t bin,
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
    
    data  -> plotOn( frame, RooFit::MarkerColor(kBlue+2), RooFit::Binning(bin) );
    if ( pdf ) pdf -> plotOn( frame, RooFit::LineColor(kRed) );
    frame -> Draw();
    
    name = Form( "Plot/data_%s.%s", identifier, extension );
    if ( pdf ) name = Form( "%s/template_%s.%s", dir, identifier, extension );
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

  TH2F* Read2DHist( std::vector <std::string> &FilePID,
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
    TH2F* hist = NULL;
    TFile* file = NULL;
    name = FilePID[0]+FilePID[i+1];
    file = TFile::Open(name.c_str());
    hist = (TH2F*)file->Get(nameHist.Data());
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

  TH3F* Read3DHist( std::vector <std::string> &FilePID,
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
    TH3F* hist = NULL;
    TFile* file = NULL;
    name = FilePID[0]+FilePID[i+1];
    file = TFile::Open(name.c_str());
    hist = (TH3F*)file->Get(nameHist.Data());
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


  void Save2DHist(TH2F* hist, PlotSettings* plotSet)
  {
    TString nameHist = hist->GetName();
    TString dir = plotSet->GetDir();
    TString ext = plotSet->GetExt();
    TString save = dir+"/"+nameHist+"."+ext;
    TCanvas *rat = new TCanvas("can","",10,10,800,600);
    TStyle *style = new TStyle();
    style->SetPalette(1);
    rat->SetFillColor(0);
    rat->cd();
    hist->Draw("COLZ");
    rat->Update();
    rat->SaveAs(save.Data());
  }

  void Save3DHist(TH3F* hist, PlotSettings* plotSet)
  {
    TString nameHist = hist->GetName();
    TString dir= plotSet->GetDir();
    TString ext= plotSet->GetExt();
    TString save = dir+"/"+nameHist+"."+ext;
    TCanvas *rat = new TCanvas("can","",10,10,800,600);
    TStyle *style = new TStyle();
    style->SetPalette(1);
    rat->SetFillColor(0);
    rat->cd();
    hist->Draw("BOX");
    rat->Update();
    rat->SaveAs(save.Data());
  }


  void Save2DComparison(TH2F* hist1, TString& l1, 
			TH2F* hist2, TString& l2, 
			TH2F* hist3, TString& l3, 
			PlotSettings* plotSet)
  {
    TLatex* legend1 = new TLatex();
    legend1->SetTextSize(0.06);
    legend1->SetTextColor(0);
    legend1->SetTextFont(132);

    TLatex* legend2 = new TLatex();
    legend2->SetTextSize(0.06);
    legend2->SetTextColor(0);
    legend2->SetTextFont(132);

    TLatex* legend3 = new TLatex();
    legend3->SetTextSize(0.06);
    legend3->SetTextColor(0);
    legend3->SetTextFont(132);

    TStyle *style = new TStyle();
    style->SetPalette(1);
    //style->SetOptLogz(1);

    TString nameHist = hist1->GetName();
    TString dir= plotSet->GetDir();
    TString ext= plotSet->GetExt();

    TString save = dir+"/"+nameHist+"_comp."+ext;
    TCanvas *rat_RW = new TCanvas("ratio_RW","",10,10,1200,400);
    rat_RW->SetFillColor(0);
    rat_RW->Divide(3,1);
    rat_RW->cd(1);
    hist1->Draw("CONT4Z");
    legend1->DrawLatex(-0.5, 0.45,l1.Data());
    rat_RW->cd(2);
    hist2->Draw("CONT4Z");
    legend2->DrawLatex(-0.5, 0.45,l2.Data());
    rat_RW->cd(3);
    style->SetOptLogz(1);
    hist3->Draw("CONT4Z");
    legend3->DrawLatex(-0.5, 0.45,l3.Data());
    ///legend2->Draw("same");
    rat_RW->Update();
    rat_RW->SaveAs(save.Data());
    
  }

  //===========================================================================
  // Weight PID histogram with weights,
  // hist1 - first histogram;
  // hist2 - first histogram;
  //===========================================================================

  TH1F* WeightHist(TH1F* hist1, TH1F* hist2, bool debug )
  {
    
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::WeightHist(...)"<<std::endl;
    Double_t w1 = hist1->GetEntries();
    Double_t w2 = hist2->GetEntries();
    Double_t w = w1+w2;
    if ( debug == true ) { std::cout<<"[INFO] weight: "<<w1<<" + "<<w2<<" which means: "<<w1/w<<" + "<<w2/w<<std::endl; }
    
    Int_t numbin = hist1 -> GetNbinsX();
    TAxis* axis=hist1->GetXaxis();
    Double_t max = axis->GetXmax();
    Double_t min = axis->GetXmin();;
    //std::cout<<"min: "<<min<<" max: "<<max<<std::endl;
    RooBinning* Bin = new RooBinning(min,max,"P");
    for (int k = 1; k < numbin; k++ )
      {
        Double_t cen = hist1 -> GetBinCenter(k);
	Double_t width = hist1 -> GetBinWidth(k);
        max = cen + width/2;
	Bin->addBoundary(max);
	//std::cout<<"k: "<<k<<" max: "<<max<<" cen: "<<cen<<" =? "<<max-width/2<<" w: "<<width<<std::endl;
      }


    //std::cout<<"hist1: bin: "<<bin1<<" in range=("<<min1<<","<<max1<<")"<<std::endl;
    //std::cout<<"hist2: bin: "<<bin2<<" in range=("<<min2<<","<<max2<<")"<<std::endl;
    //std::cout<<"hist0: bin: "<<bin<<" in range=("<<min<<","<<max<<")"<<std::endl;

    //hist1->SetBins(bin,min,max);
    hist2->SetBins(Bin->numBins(), Bin->array());
    
    TString namehist1 = hist1->GetName();
    TString nameHist = namehist1+"_weighted";
    TH1F* hist = new TH1F(nameHist.Data(), hist1->GetTitle(), Bin->numBins(), Bin->array());
    
    for(int i=0; i<numbin; i++)
      {
	Double_t bin1 = hist1->GetBinContent(i);
	Double_t bin2 = hist2->GetBinContent(i);
	Double_t bin = (bin1*w1+bin2*w2)/w;
	//std::cout<<"i: "<<i<<" bin1: "<<bin1<<" bin2: "<<bin2<<" bin: "<<bin<<std::endl;
	hist->SetBinContent(i,bin);
      }
    return hist;
    
  }

  TH1F* WeightHistFull(TString& namehist, std::vector <std::string> FileName1, std::vector <std::string> FileName2, int i, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::WeightHistFull(...)"<<std::endl;

    TH1F* hist1 = NULL;
    TH1F* hist2 = NULL;

    hist1 = ReadPIDHist(FileName1,namehist,i, debug);
    hist2 = ReadPIDHist(FileName2,namehist,i, debug);
    
    TH1F* hist = NULL;
    hist = WeightHist(hist1, hist2, debug);
    
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
      max1 = tmps[i].find("MergedTree_");
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

    for( unsigned int i =0; i< MCFileName.size(); i++ )
      {
	mode[i] = CheckMode(mode[i],debug); 
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
		    RooAbsPdf* pdf, 
		    RooRealVar* obs, 
		    TString sample, 
		    TString mode, 
		    PlotSettings* plotSet,
		    bool debug )
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::SaveTemplate(...). Saving template for background to pdf file"<<std::endl;

    if (plotSet == NULL) { plotSet = new PlotSettings("plotSet","plotSet"); }

    TCanvas*  can=NULL;
    RooPlot* frame=NULL;
    TString name,samplemode;
    samplemode =mode+"_"+sample;

    name="canvas_"+samplemode;
    can = new TCanvas(name.Data(),name.Data());
    can->cd();
    frame = (RooPlot*)obs->frame();
    TString Title = ""; 
    TString varName = obs->GetName();
 
    frame->SetLabelFont(132);
    frame->SetTitleFont(132);
    frame->GetXaxis()->SetLabelFont( 132 );
    frame->GetYaxis()->SetLabelFont( 132 );
    
    TString label = CheckObservable(varName,debug);
    frame->GetXaxis()->SetTitle(label.Data());
    
    if ( plotSet->GetTitleStatus() == true ) { TString t = GetLabel(samplemode,true,true,true,debug); Title = "#font[12]{"+t+"}"; }
    frame->SetTitle(Title.Data());
    
    name="frame_"+samplemode;
    frame->SetName(name.Data());
                                     
    Int_t bin = plotSet->GetBin();
    if ( varName.Contains("DEC") == true ) { bin = 3; }
    if ( varName.Contains("ID") == true && varName.Contains("PIDK") == false) { bin = 2; }

    if ( plotSet->GetLogStatus() == true ) { gStyle->SetOptLogy(1); }
    if (dataSet != NULL && obs != NULL) {  dataSet->plotOn(frame, RooFit::MarkerColor(plotSet->GetColorData(0)), RooFit::Binning(bin));}
    if (pdf != NULL ) { pdf->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(0)), RooFit::LineStyle(plotSet->GetStylePdf(0)));}
    frame->Draw();

    TString dir = plotSet->GetDir(); 
    
    TString ext = plotSet->GetExt();
    TString prefix = "";
    if ( dataSet != NULL &&  pdf != NULL ) { prefix = "data_with_template"; }
    else if ( pdf != NULL ) { prefix = "template"; }
    else if ( dataSet != NULL ) { prefix = "data"; }
    else { prefix = "bug"; }
    
    name=dir+"/"+prefix+"_"+varName+"_"+samplemode+"."+ext;

    can->Print(name.Data());

  }

  //===========================================================================
  // Save histogram template to the pdf file
  //==========================================================================

  void SaveTemplateHist(RooDataHist* dataSet,
			RooHistPdf* pdf,
			RooRealVar* obs,
			TString sample,
			TString mode, 
			PlotSettings* plotSet,
			bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::SaveTemplateHist(...). Saving template for background to pdf file"<<std::endl;
    if (plotSet== NULL) { plotSet = new PlotSettings("plotSet","plotSet"); }
    
    TCanvas*  can=NULL;
    RooPlot* frame=NULL;
    TString name,samplemode; 
    samplemode  =mode+"_"+sample;
    

    name="canvas_"+samplemode;
    can = new TCanvas(name.Data(),name.Data());
    can->cd();
    frame = (RooPlot*)obs->frame();
    name="frame_"+samplemode;
    frame->SetName(name.Data());
    TString Title = "";
    TString varName = obs->GetName();

    frame->SetLabelFont(132);
    frame->SetTitleFont(132);
    frame->GetXaxis()->SetLabelFont( 132 );
    frame->GetYaxis()->SetLabelFont( 132 );
    
    TString label = CheckObservable(varName,debug);
    frame->GetXaxis()->SetTitle(label.Data());

    if ( plotSet->GetTitleStatus() == true ) { TString t = GetLabel(samplemode); Title = "#font[12]{"+t+"}"; }
    frame->SetTitle(Title.Data());

    if ( plotSet->GetLogStatus() == true ) { gStyle->SetOptLogy(1); }
    if ( dataSet != NULL ) 
      {
	dataSet->plotOn(frame, RooFit::MarkerColor(plotSet->GetColorData(0)));
      }
    if( pdf != NULL ) { pdf->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(0)), RooFit::LineStyle(plotSet->GetStylePdf(0))); }
    frame->Draw();

    TString dir = plotSet->GetDir();
    TString ext = plotSet->GetExt();
    TString prefix = ""; 
    if ( dataSet != NULL &&  pdf != NULL ) { prefix = "data_with_template"; }
    else if ( pdf != NULL ) { prefix = "template"; }
    else if ( dataSet != NULL ) { prefix = "data"; }
    else { prefix = "bug"; }

    name=dir+"/"+prefix+"_"+varName+"_"+samplemode+"."+ext;

    can->Print(name.Data());
  
  }


  //===========================================================================
  // Save projection of data set  to the pdf file
  // Sample and mode are used to create name
  //==========================================================================

  void SaveDataSet(RooDataSet* dataSet, 
		   RooRealVar* obs,
		   TString sample,
		   TString mode,
		   PlotSettings* plotSet,
		   bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::SaveDataSet(...). Saving plot data set to pdf file"<<std::endl;
    SaveTemplate(dataSet, NULL, obs, sample, mode, plotSet, debug );
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
    if (mode.Contains("Lb") == true || mistag == true || mode.Contains("Bs2DsPi")==true || mode.Contains("BsDsPi") == true)
      {
	pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorBoth,1.5);
      }
    else 
      {
	pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorBoth,1.5);
      }
//    else
//      {
//	pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorBoth,3.0);
//      }
    if( pdfMC != NULL ) { if ( debug == true) std::cout<<"Create RooKeysPdf for PartRec: "<<pdfMC->GetName()<<std::endl; return pdfMC; }
    else { if ( debug == true) std::cout<<"Cannot create pdf"<<std::endl; return NULL;}
    
  }

  //===========================================================================
  // Create RooKeysPdf for dataSetMC with observable massMC.
  // Sample and mode are used to create the name of RooKeysPdf.
  //==========================================================================

  RooHistPdf* CreateHistPDF(TH1* hist,
                            RooRealVar* obs,
                            TString &name,
                            Int_t bin,
                            bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::CreateHistPDFMC(...). Create RooHistPdf"<<std::endl;
    TString n = "";
    RooHistPdf* pdfH = NULL;
    
    for (int i = 1; i< bin+1; i++)
      {
        Double_t c = hist->GetBinContent(i);
        //std::cout<<"content: "<<c<<std::endl;
        if (c < 1e-37)
          {
            hist->SetBinContent(i, 1e-37);
            // std::cout<<"set content to: "<<1e-20<<std::endl;
          }
      }
    if( hist != NULL  && debug == true) { std::cout<<"[INFO] Create histogram "<<std::endl;}
    if( hist ==NULL  && debug == true) { std::cout<<"[ERROR] Cannot create histogram "<<std::endl; }

    RooDataHist* histData = NULL;
    n = "histData_"+name;
    histData = new RooDataHist(n.Data(), n.Data(), RooArgList(*obs), hist);
    if( histData != NULL  && debug == true) { std::cout<<"[INFO] Create RooDataHist "<<histData->GetName()<<std::endl;}
    if( histData ==NULL  && debug == true) { std::cout<<"[ERROR] Cannot create RooDataHist"<<std::endl;}

    pdfH = new RooHistPdf(name.Data(), name.Data(), RooArgSet(*obs), *histData );
    if( pdfH != NULL  && debug == true) { std::cout<<"[INFO] Create RooHistPdf "<<pdfH->GetName()<<std::endl;}
    if( pdfH ==NULL  && debug == true) { std::cout<<"[ERROR] Cannot create RooHistPdf"<<std::endl;}

    return pdfH;
  }

  RooHistPdf* CreateHistPDF(RooDataSet* dataSet,
                            RooRealVar* obs,
                            TString &name,
                            Int_t bin,
                            bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::CreateHistPDFMC(...). Create RooHistPdf"<<std::endl;
    TString n = "";
    RooHistPdf* pdfH = NULL;

    TH1* hist = NULL;
    n = "hist_"+name;
    hist = dataSet->createHistogram(n.Data(), *obs, RooFit::Binning(bin));
    pdfH = CreateHistPDF(hist, obs, name, bin, debug);

    return pdfH;
  }

  RooHistPdf* CreateHistPDF(RooDataSet* dataSet1,
                            RooDataSet* dataSet2,
                            Double_t frac,
                            RooRealVar* obs,
                            TString &name,
                            Int_t bin,
                            bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::CreateHistPDFMC(...). Create RooHistPdf"<<std::endl;
    TString n = "";
    RooHistPdf* pdfH = NULL;

    TH1* hist1 = NULL;
    n = "hist1_"+name;
    hist1 = dataSet1->createHistogram(n.Data(), *obs, RooFit::Binning(bin));

    TH1* hist2 = NULL;
    n = "hist2_"+name;
    hist2 = dataSet2->createHistogram(n.Data(), *obs, RooFit::Binning(bin));

    n = "hist_"+name;
    TH1* hist = new TH1F(n.Data(), n.Data(), bin, obs->getMin(), obs->getMax());
    hist->Add(hist1, hist2, frac, 1-frac);

    pdfH = CreateHistPDF(hist, obs, name, bin, debug);

    return pdfH;
  }

  

  RooAbsPdf* CreateBinnedPDF(RooDataSet* dataSet,
			     RooRealVar* obs,
			     TString &name,
			     Int_t bin,
			     bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::CreateBinnedPDFMC(...). Create RooAbsPdf"<<std::endl;
    TString n = "";
    
    TH1* hist = NULL;
    n = "hist_"+name;
    hist = dataSet->createHistogram(n.Data(), *obs, RooFit::Binning(bin));
    for (int i = 1; i< bin+1; i++) 
      {
	Double_t c = hist->GetBinContent(i);
	if (c < 1e-37)
	  {
	    hist->SetBinContent(i, 1e-37);
	  }
      }
	
    if( hist != NULL  && debug == true) { std::cout<<"[INFO] Create histogram "<<std::endl;}
    if( hist ==NULL  && debug == true) { std::cout<<"[ERROR] Cannot create histogram "<<std::endl; }

    RooBinned1DQuinticBase<RooAbsPdf>* pdf = NULL;
    pdf = new RooBinned1DQuinticBase<RooAbsPdf>(name.Data(), name.Data(), *hist, *obs, true);
    if( pdf != NULL  && debug == true) { std::cout<<"[INFO] Create RooAbsPdf "<<pdf->GetName()<<std::endl;}
    if( pdf ==NULL  && debug == true) { std::cout<<"[ERROR] Cannot create RooAbsPDf"<<std::endl;}

    RooAbsPdf* pdfReturn = pdf;
    return pdfReturn;

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
    //obser->Print("v"); 
    if( obser != NULL ){ if ( debug == true) std::cout<<"Read observable: "<<obser->GetName()<<std::endl; return obser; }
    else{ if ( debug == true) std::cout<<"Cannot read observable"<<std::endl; return NULL;}
  }

  //===========================================================================
  // Get observable ( obs ) from workspace (work)
  //==========================================================================

  RooArgSet* GetRooArgSet(RooWorkspace* work, TString &obs, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::GetObservable("<<work->GetName()<<","<<obs<<")"<<std::endl;

    RooArgSet* obser = NULL;
    obser = (RooArgSet*)work->obj(obs.Data());
    //obser->Print("v");
    if( obser != NULL ){ if ( debug == true) std::cout<<"Read observable: "<<obser->GetName()<<std::endl; return obser; }
    else{ if ( debug == true) std::cout<<"Cannot read observable"<<std::endl; return NULL;}
  }

  //===========================================================================
  // Get observable ( obs ) from workspace (work)
  //==========================================================================

  RooCategory* GetCategory(RooWorkspace* work,
			  TString &obs, bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::GetCategory("<<work->GetName()<<","<<obs<<")"<<std::endl;

    RooCategory* obser = NULL;
    obser = (RooCategory*)work->obj(obs.Data());
    //obser->Print("v");
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
      if ( debug == true) 
	{
	  std::cout<<"Read data set: "<<data->GetName()<<" with number of entries: "<<data->numEntries() 
		   <<" and the sum of entries: "<<data->sumEntries()<<std::endl;
	}
      return data; 
    }
    else{ if ( debug == true) std::cout<<"Cannot read data set"<<std::endl; return NULL;}

  }

  RooDataSet* GetDataSet(RooWorkspace* work, RooArgSet* obs, RooCategory& sam, 
			 TString &dat, TString & sample, TString& mode, 
			 bool merge, bool debug )
  {
    
    std::vector <RooDataSet*> data;
    std::vector <TString> sm; 
    std::vector <Int_t> nEntries;
    RooDataSet* combData = NULL; 
    TString dataName = "combData";

    
    if (debug == true ){ std::cout<<"[INFO] Sample "<<sample<<". Mode "<<mode<<std::endl; }
    if ( merge == true && sample != "both") { std::cout<<"[ERROR] Option merge only possible for sample = both"<<std::endl; return NULL; }  

    std::vector <TString> s;
    std::vector <TString> m; 

    s = GetSample(sample,debug);
    m = GetMode(mode, debug );
    sm = GetSampleMode(sample, mode, false, debug);
    
    for (unsigned int i=0; i<sm.size(); i++ )
      {
	TString name = dat+sm[i]; 
	data.push_back(GetDataSet(work,name,debug));	
	nEntries.push_back(data[i]->numEntries());
      }

    if ( debug == true )
      {
	Int_t nEntries_up = 0;
	Int_t nEntries_dw = 0; 
	if ( sample == "both" ) 
	  {
	    for(unsigned int i=0; i<m.size()*s.size(); i++ )
	      {
		if( i%2 == 0 ) { nEntries_up += nEntries[i]; }
		else { nEntries_dw +=  nEntries[i]; }
	      }
	    std::cout<<"Magnet up: "<<nEntries_up<<" Magnet down: "<<nEntries_dw<<" Both polarities: "<<nEntries_up+nEntries_dw<<std::endl;
	  }
	else
	  {
	    for(unsigned int i=0; i<m.size()*s.size(); i++ )
              {
		nEntries_up += nEntries[i];
              }
	    std::cout<<"Magnet "<<sample<<": "<<nEntries_up<<std::endl;
	  }
      }
    if( merge == true )
      {
	for (unsigned int i =0; i<s.size()*m.size(); i++)
	  {
	    if(i%2 == 0) 
	      {
		data[i]->append(*data[i+1]);
	      }
	  }
		
	sm = GetSampleMode(sample, mode, true, debug);
	for (unsigned int i=0; i<m.size(); i++ )
	  {
	    sam.defineType(sm[i].Data());
	  }
 
	if (  mode == "all" )
	  {
	    
	    combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs,
				      RooFit::Index(sam),
				      RooFit::Import(sm[0].Data(),*data[0]), RooFit::Import(sm[1].Data(),*data[2]),
				      RooFit::Import(sm[2].Data(),*data[4]), RooFit::Import(sm[3].Data(),*data[6]), 
				      RooFit::Import(sm[4].Data(),*data[8]));
	  }
	else if ( mode == "3modes" or mode == "3modeskkpi" )
	  {
	    combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs,
                                      RooFit::Index(sam),
                                      RooFit::Import(sm[0].Data(),*data[0]), 
				      RooFit::Import(sm[1].Data(),*data[2]),
                                      RooFit::Import(sm[2].Data(),*data[4]));
	  }
	else
	  {
	    combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs,
                                      RooFit::Index(sam),
                                      RooFit::Import(sm[0].Data(),*data[0]));
	  }
      }
    else
      {
	for (unsigned int i=0; i<sm.size(); i++ )
	  {
	    sam.defineType(sm[i].Data());
	  }
	if ( sample == "both" )
	  {
	    if (  mode == "all" )
	      {
		combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs,
					  RooFit::Index(sam),
					  RooFit::Import(sm[0].Data(),*data[0]), RooFit::Import(sm[1].Data(),*data[1]),
					  RooFit::Import(sm[2].Data(),*data[2]), RooFit::Import(sm[3].Data(),*data[3]),
					  RooFit::Import(sm[4].Data(),*data[4]));
	    
		TString dataName2 = "combData2"; 
		RooDataSet* combData2 = new RooDataSet(dataName2.Data(), dataName2.Data(), *obs, 
						       RooFit::Index(sam),
						       RooFit::Import(sm[5].Data(),*data[5]),
						       RooFit::Import(sm[6].Data(),*data[6]), RooFit::Import(sm[7].Data(),*data[7]),
						       RooFit::Import(sm[8].Data(),*data[8]), RooFit::Import(sm[9].Data(),*data[9]));
		combData->append(*combData2); 
		
	      }
	    else if ( mode == "3modes" or mode == "3modeskkpi" )
	      {
		combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs,
					  RooFit::Index(sam),
					  RooFit::Import(sm[0].Data(),*data[0]), RooFit::Import(sm[1].Data(),*data[1]),
					  RooFit::Import(sm[2].Data(),*data[2]), RooFit::Import(sm[3].Data(),*data[3]),
					  RooFit::Import(sm[4].Data(),*data[4]), RooFit::Import(sm[5].Data(),*data[5]));
		
	      }
	    else
	      {
		combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs,
					  RooFit::Index(sam),
					  RooFit::Import(sm[0].Data(),*data[0]),
					  RooFit::Import(sm[1].Data(),*data[1]));
	      }
	  }
	else
	  {
	    if (  mode == "all" )
              {
                combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs,
                                          RooFit::Index(sam),
                                          RooFit::Import(sm[0].Data(),*data[0]), RooFit::Import(sm[1].Data(),*data[1]),
                                          RooFit::Import(sm[2].Data(),*data[2]), RooFit::Import(sm[3].Data(),*data[3]),
                                          RooFit::Import(sm[4].Data(),*data[4]));
	      }
	    else if ( mode == "3modes" or mode == "3modeskkpi" )
              {
                combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs,
                                          RooFit::Index(sam),
                                          RooFit::Import(sm[0].Data(),*data[0]), RooFit::Import(sm[1].Data(),*data[1]),
                                          RooFit::Import(sm[2].Data(),*data[2]));

	      }
            else
              {
                combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs,
                                          RooFit::Index(sam),
                                          RooFit::Import(sm[0].Data(),*data[0]));
              }

	  }
	
      }
    if( combData != NULL ){
      if ( debug == true) 
	{
	  std::cout<<"Read data set: "<<combData->GetName()<<" with number of entries: "<<combData->numEntries()
		   <<" and the sum of entries: "<<combData->sumEntries()<<std::endl;
	}
      return combData;
    }
    else{ if ( debug == true) std::cout<<"Cannot read data set"<<std::endl; return NULL;}

    
  }
  
  std::vector <TString> GetSampleMode(TString& sample, TString& mode, bool merge, bool debug )
  {
    std::vector <TString> sm;
    std::vector <TString> s;
    std::vector <TString> m;
    
    if (debug == true ){ std::cout<<"[INFO] Sample "<<sample<<". Mode "<<mode<<std::endl; }
    if ( merge == true && sample != "both") { std::cout<<"[ERROR] Option merge only possible for sample = both"<<std::endl; return sm; }

    s =  GetSample(sample,debug);
    m =  GetMode(mode, debug );
    
    for (unsigned int i=0; i<m.size(); i++ )
      {
        for(unsigned int j = 0; j<s.size(); j++ )
          {
            sm.push_back(s[j]+"_"+m[i]);
          }
      }

    if( merge == true )
      {
	TString s1 = "both";
        for (unsigned int i=0; i<m.size(); i++ )
          {
            sm[i] =s1+"_"+m[i];
          }
      }
    
    return sm; 
    
  }

  std::vector <TString>  GetSample(TString& sample, bool debug )
  {
    std::vector <TString> s;
    if ( sample == "both")  { s.push_back("up"); s.push_back("down"); }
    else { s.push_back(sample); }

    return s;
  }

  std::vector <TString>  GetMode(TString& mode, bool debug )
  {
    std::vector <TString> m;
    if ( mode == "all" ) { m.push_back("nonres"); m.push_back("phipi"); m.push_back("kstk"); m.push_back("kpipi"); m.push_back("pipipi"); }
    else if (mode == "3modeskkpi") {  m.push_back("nonres"); m.push_back("phipi"); m.push_back("kstk"); }
    else if (mode == "3modes" ) { m.push_back("kkpi"); m.push_back("kpipi"); m.push_back("pipipi"); }
    else { m.push_back(mode); }
    return m;
  }

  std::vector <Int_t> GetEntriesCombData(RooWorkspace* work, 
					 TString &dat, TString & sample, TString& mode,
					 bool merge, bool debug )
  {
    std::vector <RooDataSet*> data;
    std::vector <TString> sm;
    std::vector <Int_t> nEntries;
    std::vector <Int_t> nE; 

    if (debug == true ){ std::cout<<"[INFO] Sample "<<sample<<". Mode "<<mode<<std::endl; }
    if ( merge == true && sample != "both") { std::cout<<"[ERROR] Option merge only possible for sample = both"<<std::endl; return nEntries; }

    std::vector <TString> s;
    std::vector <TString> m;

    s = GetSample(sample,debug);
    m = GetMode(mode, debug );
    sm = GetSampleMode(sample, mode, false, debug);

    for (unsigned int i=0; i<sm.size(); i++ )
      {
        TString name = dat+sm[i];
        data.push_back(GetDataSet(work,name,debug));
        nEntries.push_back(data[i]->numEntries());
      }
    
    if( merge == true )
      {
        for (unsigned int i =0; i<s.size()*m.size(); i++)
          {
            if(i%2 == 0)
              {
                nEntries[i] += nEntries[i+1];
		nE.push_back(nEntries[i]); 
              }
	  }
      }
   
    return nE; 

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
      if ( debug == true) work->Print();
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
	polarity = "both"; 
      }
    if ( debug == true) std::cout<<"[INFO] Sample: "<<polarity<<std::endl;
    return polarity;
  }  

  TString CheckPolarity(TString& check, bool debug)
  {
    TString polarity;
    if (check.Contains("MD") == true  || check.Contains("down") == true || check.Contains("dw") == true || check.Contains("Down") == true || 
	check.Contains("md") == true)
      {
        polarity = "down";
      }
    else if ( check.Contains("MU") == true || check.Contains("up") == true || check.Contains("Up") == true || check.Contains("mu") == true )
      {
        polarity = "up";
      }
    else
      {
        polarity = "both";
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
    else if ( check.find("hhhpi0") != std::string::npos || check.find("HHHPi0") != std::string::npos ||
              check.find("hhhPi0") != std::string::npos || check.find("HHHpi0") != std::string::npos)
      {
        dmode = "hhhpi0";
      }
    else 
      {
        dmode = "";
      }
    if ( debug == true) std::cout<<"[INFO] Sample: "<<dmode<<std::endl;
    return dmode;
  }

  TString CheckDMode(TString& check, bool debug)
  {
    TString dmode;
    if (check.Contains("KKpi") == true  || check.Contains("KKPi") == true || check.Contains("kkpi") == true )
      {
	dmode = "kkpi";
      }
    else if ( check.Contains("Kpipi") == true || check.Contains("KPiPi") == true || check.Contains("kpipi") == true)
      {
        dmode = "kpipi";
      }
    else if ( check.Contains("pipipi") == true || check.Contains("PiPiPi") == true)
      {
        dmode = "pipipi";
      }
    else if ( check.Contains("hhhpi0") == true || check.Contains("HHHPi0") == true ||
              check.Contains("hhhPi0") == true || check.Contains("HHHpi0") == true)
      {
        dmode ="hhhpi0";
      }
    else
      {
	dmode = "";
      }
    if ( debug == true) std::cout<<"[INFO] Sample: "<<dmode<<std::endl;
    return dmode;
  }

  TString CheckKKPiMode(std::string& check, bool debug)
  {
    TString dmode;
    if (check.find("nonRes") != std::string::npos  || check.find("NonRes") != std::string::npos 
	|| check.find("nonres") != std::string::npos || check.find("nonRes") != std::string::npos )
      {
        dmode = "nonres";
      }
    else if ( check.find("PhiPi") != std::string::npos || check.find("phipi") != std::string::npos 
	      || check.find("Phipi") != std::string::npos || check.find("phiPi") != std::string::npos)
      {
        dmode = "phipi";
      }
    else if ( check.find("KstK") != std::string::npos || check.find("kstk") != std::string::npos ||
	      check.find("Kstk") != std::string::npos || check.find("kstK") != std::string::npos)
      {
        dmode = "kstk";
      }
    else if ( check.find("hhhpi0") != std::string::npos || check.find("HHHPi0") != std::string::npos ||
              check.find("hhhPi0") != std::string::npos || check.find("HHHpi0") != std::string::npos)
      {
	dmode = "hhhpi0";
      }
    else
      {
        dmode = "";
      }
    if ( debug == true) std::cout<<"[INFO] Sample: "<<dmode<<std::endl;
    return dmode;
  }


  TString CheckKKPiMode(TString& check, bool debug)
  {
    TString kkpimode;
    if (check.Contains("nonres") == true  || check.Contains("NonRes") == true || check.Contains("nonRes") == true || check.Contains("Nonres") == true )
      {
        kkpimode = "nonres";
      }
    else if ( check.Contains("phipi") == true || check.Contains("Phipi") == true || check.Contains("PhiPi") == true || check.Contains("phiPi") == true)
      {
        kkpimode = "phipi";
      }
    else if ( check.Contains("kstk") == true || check.Contains("KstK") == true || check.Contains("kstK") == true || check.Contains("Kstk") == true)
      {
        kkpimode = "kstk";
      }
    else if ( check.Contains("hhhpi0") == true || check.Contains("HHHPi0") == true || 
	      check.Contains("hhhPi0") == true || check.Contains("HHHpi0") == true)
      {
	kkpimode ="hhhpi0";
      }
    else
      {
	kkpimode = "";
      }
    if ( debug == true) std::cout<<"[INFO] Sample: "<<kkpimode<<std::endl;
    return kkpimode;
  }

  std::string CheckMode(std::string& check, bool debug )
  {
    std::string mode;
    std::string Bs = "";
    std::string Ds = "";
    std::string Bach = "";

    if ( check.find("Lb") != std::string::npos ||
	 check.find("lambdab") != std::string::npos ||
	 check.find("Lambdab") != std::string::npos  ){ Bs="Lb";}
    else if( check.find("Bs") != std::string::npos || check.find("bs") != std::string::npos) { Bs = "Bs"; }
    else if (( check.find("Bd") != std::string::npos || check.find("bd") != std::string::npos ) && check.find("ambda") == std::string::npos )
      { Bs="Bd"; }
    else { Bs="Comb";}

    if (check.find("Lc") != std::string::npos ||
	check.find("lambdac") != std::string::npos ||
	check.find("Lambdac") != std::string::npos) { Ds = "Lc";}
    else if (check.find("Dsst") != std::string::npos || check.find("dsst") != std::string::npos)
      { Ds ="Dsst";}
    else if ( (check.find("Ds") != std::string::npos  || check.find("ds") != std::string::npos) && 
	 (check.find("Dsst") == std::string::npos || check.find("dsst") == std::string::npos ))
      { Ds = "Ds";}
    else if (( check.find("D") != std::string::npos  || check.find("d") != std::string::npos )  &&
	     (check.find("Ds") == std::string::npos  || check.find("ds") == std::string::npos) && check.find("ambda") == std::string::npos) 
      {Ds = "D";}
    else { Ds ="bkg";}

    if ( check.find("Pi") != std::string::npos || check.find("pi") != std::string::npos) { Bach = "Pi"; }
    else if( ( check.find("P") != std::string::npos || check.find("p") != std::string::npos ) && 
	     ( check.find("Pi") == std::string::npos || check.find("pi") == std::string::npos))
      {Bach = "p";}
    else if( (check.find("K") != std::string::npos || check.find("k") != std::string::npos )&& 
	     (check.find("Kst") == std::string::npos || check.find("kst") == std::string::npos) )
      {Bach = "K";}
    else if( check.find("Kst") != std::string::npos || check.find("kst") != std::string::npos ) {Bach ="Kst";}
    else if( check.find("Rho") != std::string::npos || check.find("rho") != std::string::npos ) {Bach = "Rho";}
    else { Bach ="";}

    mode = Bs+"2"+Ds+Bach;
    if (debug == true )
      {
	if ( mode != check )
	  {
	    std::cout<<"[INFO] Changed mode label from: "<< check <<" to: "<<mode<<std::endl;
	  } 
      }
    return mode; 
  }
  
  TString GetLabel(TString& mode, bool bs, bool ds, bool pol, bool debug)
  {
    TString Bs;
    TString ar = "#rightarrow";
    TString Ds;
    TString Bach;
    TString sample;
    TString DsState = "";
    TString DsStateTex = "";

    sample = CheckPolarity(mode, debug);
    DsState = CheckDMode(mode, debug);
    if ( DsState == "" || DsState == "kkpi" ) { DsState = CheckKKPiMode(mode, debug); } 

    if ( mode.Contains("Lb") == true || mode.Contains("lambdab") == true || mode.Contains("Lambdab") == true  ){ Bs="#Lambda_{b}";}
    else if( mode.Contains("Bs") == true || mode.Contains("bs") == true) { Bs = "B_{s}"; }
    else if ( mode.Contains("Bd") == true || mode.Contains("bd") == true ){ Bs="B_{d}"; }
    else { Bs="Comb";}

    if (mode.Contains("Lc") == true || mode.Contains("Lambdac") == true || mode.Contains("lambdac") == true) { Ds = "#Lambda_{c}";}
    else if (mode.Contains("Dsst") == true || mode.Contains("dsst") == true){ Ds ="D^{*}_{s}";}
    else if ( (mode.Contains("Ds") == true  || mode.Contains("ds") == true) && (mode.Contains("Dsst") != true || mode.Contains("dsst") != true )) 
      { Ds = "D_{s}";}
    else if ((mode.Contains("D")==true || mode.Contains("d") == true )  &&  
	     ( mode.Contains("Ds") != true || mode.Contains("ds") == true )) {Ds = "D";}
    else { Ds ="bkg";}

    if ( mode.Contains("Pi") == true || mode.Contains("pi") == true ) { Bach = "#pi"; }
    else if( (mode.Contains("p") == true || mode.Contains("P") == true ) && (mode.Contains("pi") == true || mode.Contains("Pi") == true )) 
      {Bach = "p";}
    else if( (mode.Contains("K") == true || mode.Contains("k") == true )&& (mode.Contains("Kst")!=true || mode.Contains("kst") != true) ) 
      {Bach = "K";}
    else if( ( mode.Contains("Kst") == true || mode.Contains("kst") == true ) ) {Bach ="K^{*}";}
    else if( mode.Contains("Rho") == true || mode.Contains("rho") == true ) {Bach = "#rho";}
    else { Bach ="";}

    if ( DsState.Contains("kkpi") == true ) { DsStateTex = Ds+ar+" KK#pi"; }
    else if ( DsState.Contains("kstk") == true ) { DsStateTex = Ds+ar+" KstK";}
    else if ( DsState.Contains("phipi") == true ) { DsStateTex = Ds+ar+" #phi #pi";}
    else if ( DsState.Contains("nonres") == true ) { DsStateTex = Ds+ar+"KK#pi (Non Resonant)";}
    else if ( DsState.Contains("kpipi") == true ) { DsStateTex = Ds+ar+" K#pi#pi";}
    else if ( DsState.Contains("pipipi") == true ) { DsStateTex = Ds+ar+" #pi#pi#pi";}
    else if ( DsState.Contains("hhhpi0") == true ) { DsStateTex = Ds+ar+" hhh#pi^{0}"; }
    else { DsStateTex = ""; }
    
    TString tex = "";
    if ( mode.Contains("Comb") == true ) 
      { 
	if ( bs == true )
	  {
	    tex += Bs+" "+Ds+" ";
	  }
      } 
    else 
      { 
	if ( bs == true )
	  {
	    tex +=Bs+" "+ar+" "+Ds+Bach+" ";
	  }
      }

    if ( ds == true )
      {
	tex += DsStateTex+" ";
      }
    if ( pol == true )
      {
	tex += sample;
      }

        
    return tex;
  }

  
  TString CheckBDTGBin(TString& check, bool debug)
  {
    TString BDTGbin;
    if (check.Contains("BDTG1") == true)
      {
	BDTGbin = "BDTG1";
      }
    else if ( check.Contains("BDTG2") == true)
      {
        BDTGbin = "BDTG2";
      }
    else if ( check.Contains("BDTG3") == true )
      {
        BDTGbin = "BDTG3";
      }
    else if ( check.Contains("BDTGA") == true )
      {
	BDTGbin= "BDTGA";
      }
    else if ( check.Contains("BDTGC") == true )
      {
	BDTGbin= "BDTGC";
      }
    else
      {
        BDTGbin = "";
      }
    if ( debug == true) std::cout<<"[INFO] BDTG bin: "<<BDTGbin<<std::endl;
    return BDTGbin;
  }

  
  TString CheckObservable(TString& check, bool debug)
  {
    TString label = "";
    if( check.Contains("lab0_MassFitConsD_M") == true || check.Contains("lab0_MM") == true  ||
	(check.Contains("Bs") == true && check.Contains("Mass") == true) ) { label = "mass B_{(s)} [MeV/c^{2}]"; }
    else if ( check.Contains("Ds_MM") == true || check.Contains("lab2_MM") == true ) { label = "mass D_{(s)} [MeV/c^{2}]";}
    else if ( check.Contains("TAGDECISION") == true || check.Contains("DEC") == true ) 
      { 
	if ( check.Contains("SS_nnetKaon") == true )  { label = "tagging decision SS [1]"; }
	else if ( check.Contains("TAGDECISION_OS") == true )  { label = "tagging decision OS [1]"; }
	else { label = "tagging decision [1]"; }
      }
    else if ( check.Contains("TAGOMEGA") == true || check.Contains("PROB") == true) 
      {
	if ( check.Contains("SS_nnetKaon") == true )  { label = "#omega SS [1]"; }
	else if( check.Contains("TAGOMEGA_OS") == true )  { label = "#omega OS [1]"; }
	else { label = "#omega [1]"; }
      }
    else if ( check.Contains("LifetimeFit_ctau") == true || check.Contains("TAU") == true ||  check.Contains("TRUETAU") == true ) 
      {label ="t [ps]"; }
    else if ( check.Contains("ID") == true && check.Contains("PIDK") == false && 
	      ( check.Contains("lab1") == true || check.Contains("Bac") ==true) ) {label ="bachelor ID [1]"; }
    else if ( check.Contains("PIDK") == true && ( check.Contains("lab1") == true || check.Contains("Bac") ==true) ) {label ="bachelor PIDK [1]"; }
    else if ( check.Contains("_PT") == true ) {label ="log(p_{t}) [MeV/c]"; }
    else if ( check.Contains("_P") == true && check.Contains("_PT") == false ) {label ="log(p) [MeV/c]"; }
    else if ( check.Contains("nTracks") == true ) {label ="log(nTracks) [1]"; }
    else { label = check; } 
    
    if ( debug == true) std::cout<<"[INFO] Observable label: "<<label<<std::endl;

    return label;
  }

  TString CheckBachelor(TString check, bool debug)
  {
    TString bachelor = "";
    
    if( check.Contains("CombPi") == true ) { TString s1 = "CombPi"; TString s2 = ""; check.ReplaceAll(s1,s2); }
    if( check.Contains("CombK") == true ) { TString s1 = "CombK"; TString s2 = ""; check.ReplaceAll(s1,s2); }
    if( check.Contains("MC BsDsK") == true ) { TString s1 = "BsDsK"; TString s2 = ""; check.ReplaceAll(s1,s2); }
    if( check.Contains("MC BsDsPi") == true ) { TString s1 = "BsDsPi"; TString s2 = ""; check.ReplaceAll(s1,s2); }
 
    if( check.Contains("pion") == true || check.Contains("Pion") == true ) 
	
      {
	bachelor = "Pi";
      }
    else if ( check.Contains("kaon") == true || check.Contains("Kaon") == true)  
      
      {
	bachelor = "K";
      }
    else if ( check.Contains("proton") == true || check.Contains("Proton") == true )
      {
	bachelor = "P";
      }

    if ( debug == true) std::cout<<"[INFO] Sample: "<<bachelor<<std::endl;

    return bachelor; 
  }

  //===========================================================================
  // Get coefficient for acceptance
  //==========================================================================

  RooArgList* GetCoeffFromBinning(RooBinning* binning, RooRealVar* time, bool debug)
  {
    RooArgList* list=NULL;
    Double_t max = time->getMax();
    Double_t min = time->getMin(); 
    if (debug) std::cout<<"Min of time: "<<min<<" max of time: "<<max<<std::endl; 
    
    Int_t numB = binning->numBins();
    Double_t x2(0.0), x1(0.0);
    
    if(max > binning->binHigh(numB-1) )
      {
	x2 = binning->binHigh(numB-1);
	x1 = binning->binHigh(numB-2);
      }
    else
      {
	return NULL;
      }

    Double_t c2(0.0), c1(0.0);
    c2 = 1 - (max - x2)/(x1-x2);
    c1 = (max - x2)/(x1-x2);
    
    if (debug) std::cout<<"xN = "<<max<<" xN-1 = "<<x2<<" xN-2 = "<<x1<<std::endl;
    if (debug) std::cout<<"cN-1 = "<<c2<<" cN-2 = "<<c1<<std::endl;

    RooConstVar* c2Var = new RooConstVar("c2Var", "c2Var", c2);
    RooConstVar* c1Var = new RooConstVar("c1Var", "c1Var", c1);
    
    list = new RooArgList(*c1Var,*c2Var);
    return list;
  }

  double pe_from_pid(int pid, double px, double py, double pz)
  {
    // some constants
    const double BSMASS(5366.77), BDMASS(5279.58), DSMASS(1968.49),
      DSSTMASS(2112.3), DMASS(1869.62), PIMASS(139.57018), KMASS(493.677),
      KSTMASS(891.66), PI0MASS(134.9766), LBMASS(5619.4), LCMASS(2286.46),
      PMASS(938.272046), RHOMASS(775.49);

    double p2(px*px + py*py + pz*pz), mass(0.0);
    switch (std::abs(pid)) {
    case 531:		// Bs
      mass = BSMASS; break;
    case 511:		// Bd
      mass = BDMASS; break;
    case 431:		// Ds+
      mass = DSMASS; break;
    case 411:		// D+
      mass = DMASS; break;
    case 433:		// Dsst
      mass = DSSTMASS; break;
    case 321:		// K
      mass = KMASS; break;
    case 211:		// Pi
      mass = PIMASS; break;
    case 5122:	// Lb
      mass = LBMASS; break;
    case 2212:	// p
      mass = PMASS; break;
    case 4122:	// Lc+
      mass = LCMASS; break;
    case 213:		// Rho(770)+
      mass = RHOMASS; break;
    case 111:		// Pi0
      mass = PI0MASS; break;
    case 22:		// photon
    default:
      mass = 0.0;
    }
    return std::sqrt(mass*mass + p2);
  }
} //end of namespace
