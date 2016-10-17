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
#include <utility>

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
#include "TObjArray.h"
 
// B2DXFitters includes
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/DecayTreeTupleSucksFitter.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"
#include "B2DXFitters/PlotSettings.h"


#define DEBUG(COUNT, MSG)                                           \
  std::cout << "SA-DEBUG: [" << COUNT << "] (" << __func__ << ") "  \
  << MSG << std::endl;                                              \
  COUNT++;

#define ERROR(COUNT, MSG)                                           \
  std::cerr << "SA-ERROR: [" << COUNT << "] (" << __func__ << ") "  \
  << MSG << std::endl;                                              \
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
    //std::cout<<"signature: "<<sig<<std::endl; 

    if (myfile.is_open())
    {
	
      while(myfile.good())
      {
	     
        getline (myfile,line);
        //std::cout<<"poczatek"<<line<<"koniec"<<std::endl; 
        if(line == sig.Data() ){
          while( line != "###" ){
            getline (myfile,line);
            if( line != "###"){ FileName.push_back(line.c_str());}
          }
        }
      }
    }
    else { if ( debug == true) std::cout<<"Unable to open a file"<<std::endl;}
    /*
      if ( debug == true ) { 
      std::cout<<"file0"<<FileName[0]<<std::endl;
      std::cout<<"file0"<<FileName[1]<<std::endl;
      std::cout<<"file0"<<FileName[2]<<std::endl;
      std::cout<<"file0"<<FileName[3]<<std::endl;
      std::cout<<"file0"<<FileName[4]<<std::endl;
      }*/
  }

  Int_t CheckNumberOfBackgrounds(TString& filesDir, TString& sig, bool debug)
  {
    std::string line;
    std::ifstream myfile(filesDir.Data());
    Int_t count=0; 

    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::CheckNumberOfBackgrounds(...)"<<std::endl;

    if (myfile.is_open())
    {
      while(myfile.good())
      {
        getline (myfile,line);
        if(line == sig.Data() ){
          while( line != "###" ){
            getline (myfile,line);
            if ( line.find("}") < line.size() ) { count++; }
          }
        }
      }
    }
    else { if ( debug == true) std::cout<<"Unable to open a file: "<<filesDir<<std::endl;}
    myfile.close(); 
    return count; 
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
    if ( debug == true) std::cout<<"[INFO] file to open "<<name[0]<<std::endl; 

    file = TFile::Open(name[0].c_str());
    tree = (TTree*) file->Get(FileName[i+3].c_str());
    
    if ( debug == true){
      std::cout<<"[INFO] file content:"<<std::endl;
      file->ls();
      std::cout<<"[INFO] tree to read "<<FileName[i+3].c_str()<<std::endl;
    }
    
    if  ( tree ==  NULL ) {
      std::cout<<" Cannot open file: "<<FileName[0]+FileName[i+1]<<std::endl;
      return NULL;
    }
    else {  
      if ( debug == true)
      {
        //std::cout<<"Open file: "<<FileName[0]+FileName[i+1]<<std::endl;
        std::cout<<"[INFO] with Tree: "<<tree->GetName()<<std::endl;
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
    can->SetLeftMargin(0.15);
    can->SetBottomMargin(0.15);
    can->SetTopMargin(0.05);
    can->SetRightMargin(0.05);


    frame = (RooPlot*)obs->frame();
    TString Title = ""; 
    TString varName = obs->GetName();
    if ( varName.Contains("[0]") == true ) { varName.ReplaceAll("[0]",""); } 
      
    frame->SetLabelFont(132);
    frame->SetTitleFont(132);
    frame->GetXaxis()->SetLabelFont( 132 );
    frame->GetYaxis()->SetLabelFont( 132 );
    frame->GetXaxis()->SetLabelSize( 0.06 );
    frame->GetYaxis()->SetLabelSize( 0.06 );
    frame->GetXaxis()->SetTitleSize( 0.06 );
    frame->GetYaxis()->SetTitleSize( 0.06 );
    frame->GetYaxis()->SetTitleOffset( 1.10 );
    if ( dataSet == NULL ) { frame->GetYaxis()->SetTitle(""); }

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
    if (dataSet != NULL && obs != NULL) 
    {  
      dataSet->plotOn(frame, RooFit::MarkerColor(plotSet->GetColorData(0)), RooFit::Binning(bin));
    }
    if (pdf != NULL ) { pdf->plotOn(frame, RooFit::LineColor(plotSet->GetColorPdf(0)), RooFit::LineStyle(plotSet->GetStylePdf(0)));}
    if ( dataSet == NULL ) { frame->GetYaxis()->SetTitle(""); frame->GetYaxis()->SetTitleColor(kWhite);}
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
    if(debug == true) std::cout<<"[INFO] ==> GeneralUtils.TreeCut(...): creating temp tree "<<name.Data()<<std::endl;
    treetmp = new TTree(name.Data(),name.Data());
    name = "Trash/Cut_file_"+name2+".root";
    if(debug == true) std::cout<<"[INFO] ==> GeneralUtils.TreeCut(...): creating temp file "<<name.Data()<<std::endl;
    tfiletmp = new TFile(name.Data(),"recreate");
    treetmp->SetDirectory(tfiletmp);
    if(debug == true) std::cout<<"[INFO] ==> GeneralUtils.TreeCut(...): start to copy tree with selection "<<std::endl;
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
                          TString &mode,
                          Double_t rho,
                          TString mirror, 
                          bool debug)
  {
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::CreatePDFMC(...). Create RooKeysPdf for MC"<<std::endl;

    RooKeysPdf* pdfMC = NULL;
    TString name3, name2, name;
    name3="Pdf_m_"+sample;
    name2= mode+name3;
    name="PhysBkg"+name2;
    
    if (mirror == "Both")
    {
      pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorBoth,rho);
    }
    else if ( mirror == "Left" )
    {
      pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorLeft,rho);
    }
    else if ( mirror == "Right" )
    {
      pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorRight,rho);
    }
    else if ( mirror == "No" )
    {
      pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::NoMirror,rho);
    }
    else if (mirror == "AsymLeftRight")
    {
      pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorAsymLeftRight,rho);
    }
    else if ( mirror == "AsymLeft" )
    {
      pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorAsymLeft,rho);
    }
    else if ( mirror == "AsymRight" )
    {
      pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorAsymRight,rho);
    }
    else if ( mirror == "LeftAsymRigh" )
    {
      pdfMC = new RooKeysPdf(name.Data(),name.Data(),*massMC,*dataSetMC,RooKeysPdf::MirrorLeftAsymRight,rho);
    }


    if( pdfMC != NULL ) { if ( debug == true) std::cout<<"Create RooKeysPdf for PartRec: "<<pdfMC->GetName()<<std::endl; return pdfMC; }
    else { if ( debug == true) std::cout<<"Cannot create pdf"<<std::endl; return NULL;}
    
  }
  RooKeysPdf* CreatePDFMC(RooDataSet* dataSetMC,
                          RooRealVar* massMC,
                          TString &sample,
                          TString &mode,
                          bool debug)
  {
    RooKeysPdf* pdf = CreatePDFMC(dataSetMC,massMC, sample, mode, 1.5, "Both", debug);
    return pdf; 
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
    if(debug == true) std::cout<<"[INFO] ==> GeneralUtils::CreateHistPDFMC(...). Bins: "<<bin<<", Min: "<<obs->getMin()<<", Max: "<<obs->getMax()<<std::endl;
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
    TString dat_ = TString(dat.Data());
    data = (RooDataSet*)work->data(dat.Data());
    if( data != NULL ){ 
      if ( debug == true) 
      {
        std::cout<<"Read data set: "<<data->GetName()<<" with number of entries: "<<data->numEntries() 
                 <<" and the sum of entries: "<<data->sumEntries()<<std::endl;
      }
      return data; 
    }
    else{
      if ( debug == true) std::cout<<"Cannot read data set; trying to remove 2 from the name (if there)"<<std::endl;
      if(dat_.Contains("2"))
      {        
        dat_.ReplaceAll("2",""); 
        if ( debug == true) std::cout<<"New name: "<<dat_.Data()<<std::endl;
      }
      data = (RooDataSet*)work->data(dat_.Data());
      if (data != NULL){
        if ( debug == true){
          std::cout<<"Read data set: "<<data->GetName()<<" with number of entries: "<<data->numEntries()
                   <<" and the sum of entries: "<<data->sumEntries()<<std::endl;
        }
        return data;
      }
      else
      {
        if ( debug == true) std::cout<<"Cannot read dataset; trying to switch to upper/lower case names"<<std::endl;
        
        if(dat_.Contains("KPiPi") == true) dat_.ReplaceAll("KPiPi","kpipi");
        else if(dat_.Contains("KKPi") == true) dat_.ReplaceAll("KKPi","kkpi");
        else if(dat_.Contains("PiPiPi") == true) dat_.ReplaceAll("PiPiPi","pipipi");
        else if(dat_.Contains("NonRes") == true) dat_.ReplaceAll("NonRes","nonres");
        else if(dat_.Contains("PhiPi") == true) dat_.ReplaceAll("PhiPi","phipi");
        else if(dat_.Contains("KstK") == true) dat_.ReplaceAll("KstK","kstk");
        else if(dat_.Contains("HHHPi0") == true) dat_.ReplaceAll("HHHPi0","hhhpi0");
        else if(dat_.Contains("kpipi") == true) dat_.ReplaceAll("kpipi","KPiPi");
        else if(dat_.Contains("kkpi") == true) dat_.ReplaceAll("kkpi","KKPi");
        else if(dat_.Contains("pipipi") == true) dat_.ReplaceAll("pipipi","PiPiPi");
        else if(dat_.Contains("nonres") == true) dat_.ReplaceAll("nonres","NonRes");
        else if(dat_.Contains("phipi") == true) dat_.ReplaceAll("phipi","PhiPi");
        else if(dat_.Contains("kstk") == true) dat_.ReplaceAll("kstk","KstK");
        else if(dat_.Contains("hhhpi0") == true) dat_.ReplaceAll("hhhpi0","HHHPi0");
      
        if ( debug == true) std::cout<<"New name: "<<dat_.Data()<<std::endl;
        
        data = (RooDataSet*)work->data(dat_.Data());
        if(data != NULL){
          if ( debug == true){
            std::cout<<"Read data set: "<<data->GetName()<<" with number of entries: "<<data->numEntries()
                     <<" and the sum of entries: "<<data->sumEntries()<<std::endl; 
          }
          return data; 
        }     
        else{  
          if ( debug == true) std::cout<<"Cannot read data set with name "<<dat_.Data()<<std::endl; 
          return NULL;
        }
      }
    }
  }
  
  /*
    RooDataSet* GetDataSet(RooWorkspace* work, RooArgSet* obs, RooCategory& sam, 
    TString &dat, TString & sample, TString& mode, 
    TString &merge, bool debug )
    {
    
    std::vector <RooDataSet*> data;
    std::vector <TString> sm; 
    std::vector <Int_t> nEntries;
    RooDataSet* combData = NULL; 
    TString dataName = "combData";

    
    if (debug == true ){ std::cout<<"[INFO] Sample "<<sample<<". Mode "<<mode<<std::endl; }
    if ( (merge == "pol" || m&& sample != "both") { std::cout<<"[ERROR] Option merge only possible for sample = both"<<std::endl; return NULL; }  

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
    if ( debug == true ) { std::cout<<"Magnet up: "<<nEntries_up<<" Magnet down: "<<nEntries_dw<<" Both polarities: "<<nEntries_up+nEntries_dw<<std::endl;}
	  }
    else
	  {
    for(unsigned int i=0; i<m.size()*s.size(); i++ )
    {
		nEntries_up += nEntries[i];
    }
    if ( debug == true ) {  std::cout<<"Magnet "<<sample<<": "<<nEntries_up<<std::endl;}
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
  */  
  RooDataSet* GetDataSet(RooWorkspace* work, RooArgSet* obs, RooCategory& sam,
                         TString &dat, TString & sample, TString& mode, TString& year, TString& hypo,
                         TString merge, bool debug )
  {

    if ( debug == true ) {
      std::cout<<"[INFO] GetDataSet(...)"<<std::endl; 
      if (debug == true ){ std::cout<<"[INFO] Sample: "<<sample<<", Mode: "<<mode<<", Year: "<<year<<", Hypo: "<<hypo<<", Merge: "<<merge<<std::endl; }
      if ( (merge == "pol" || merge == "both") && sample != "both") { std::cout<<"[ERROR] Option --merge pol only possible for --pol both"<<std::endl; return NULL; }
      if ( (merge == "year" || merge == "both") && year != "run1") { std::cout<<"[ERROR] Option --merge year only possible for --year run1"<<std::endl; return NULL; }
    }
    std::vector <RooDataSet*> data;
    std::vector <TString> sm;
    std::vector <Int_t> nEntries;
    RooDataSet* combData = NULL;
    TString dataName = "combData";
    
    /*std::vector <TString> s;
    std::vector <TString> m;
    std::vector <TString> y;
    std::vector <TString> h;

    s = GetSample(sample, "", debug);
    m = GetMode(mode, debug );
    y = GetDataYear(year, "", debug );
    h = GetHypo(hypo, debug);*/

    TString newmerge;

    if (!merge.Contains("already")){ //usual case
      sm = GetSampleModeYearHypo(sample, mode, year, hypo, "", debug);
      newmerge = merge;
    }    

    else{ // if "alreadyyear/pol/both", the samples are "already" merged in the workspace
      sm = GetSampleModeYearHypo(sample, mode, year, hypo, merge, debug);
      newmerge = "";
    }
    
    for (unsigned int i=0; i<sm.size(); i++ )
    {
      if( debug )
      {
        std::cout<<"[INFO] ==> GetDataSet(...): start to collect datasets from workspace"<<std::endl;
      }
      TString name = dat+sm[i];
      data.push_back(GetDataSet(work,name,debug));
      nEntries.push_back(data[i]->numEntries());
    }

    if( newmerge != "" )
    {
      std::vector <RooDataSet*> dataOut;
      std::vector <RooDataSet*> dataOutTmp;
      for (unsigned int i=0; i<sm.size(); i++ )
      {
        TString y3 = sm[i];
        TString y1 = sm[i];
        TString y2 = ""; 
        if ( newmerge == "pol" || newmerge == "both") 
	      {
          y2 = y1.ReplaceAll("up","down");
	      }
        else
	      {
          y2 = y1.ReplaceAll("2011","2012");
	      }
        // std::cout<<"y3: "<<y3<<" y1: "<<y1<<std::endl; 
        if ( ( (newmerge == "pol" || newmerge == "both") && y3.Contains("down") == false) || ( newmerge == "year" && y3.Contains("2011")))
	      {
          for (unsigned int j=0; j<sm.size(); j++ )
          {
            if ( sm[j] == y2 )
            {
              data[i]->append(*data[j]);
              nEntries[i] += nEntries[j];
              if ( debug == true ) { std::cout<<"[INFO] Adding "<<data[i]->GetName()<<" "<<data[j]->GetName()
                                              <<" "<<data[i]->numEntries()<<std::endl; }
              TString nD = data[i]->GetName();
              if ( newmerge == "pol" || newmerge == "both")
              {
                nD.ReplaceAll("up","both");
              }
              else
              {
                nD.ReplaceAll("2011","run1");
              }
              data[i]->SetName(nD.Data());
              if ( debug == true ) { std::cout<<"[INFO] New data name: "<<data[i]->GetName()<<std::endl;}
              dataOutTmp.push_back(data[i]); 
            }
          }
	      }
      }
      
      if ( newmerge == "both" )
      {
        sm = GetSampleModeYearHypo(sample, mode, year, hypo, "pol", debug);
        for (unsigned int i=0; i<sm.size(); i++ )
        {
          if ( debug == true ) { std::cout<<"[INFO] In dataOutTmp name: "<<dataOutTmp[i]->GetName()<<" with entries " << dataOutTmp[i]->numEntries()<<std::endl;}
	      }
        
        for (unsigned int i=0; i<sm.size(); i++ )
	      {
          TString y3 = sm[i];
          TString y1 = sm[i];
          TString y2 = y1.ReplaceAll("2011","2012");
          if (  y3.Contains("2011"))
          {
            for (unsigned int j=0; j<sm.size(); j++ )
            {
              if ( sm[j] == y2 )
              {
                dataOutTmp[i]->append(*dataOutTmp[j]);
                nEntries[i] += nEntries[j];
                if ( debug == true ) { std::cout<<"[INFO] Adding "<<dataOutTmp[i]->GetName()<<" "<<dataOutTmp[j]->GetName()
                                                <<" "<<dataOutTmp[i]->numEntries()<<std::endl; }
                TString nD = dataOutTmp[i]->GetName();
                nD.ReplaceAll("2011","run1");
                dataOutTmp[i]->SetName(nD.Data());
                if ( debug == true ) { std::cout<<"[INFO] New data name: "<<dataOutTmp[i]->GetName()<<std::endl;}
                dataOut.push_back(dataOutTmp[i]);
              }
            }
            
          }
          
	      }
      }
      else
      {
        dataOut = dataOutTmp;
      }

      sm = GetSampleModeYearHypo(sample, mode, year, hypo, newmerge, debug);
      for (unsigned int i=0; i<sm.size(); i++ )
      {
        sam.defineType(sm[i].Data());
        if ( debug == true ) { std::cout<<"In dataOut name: "<<dataOut[i]->GetName()<<" with entries " << dataOut[i]->numEntries()<<std::endl;}
      }
      //const RooArgSet* obs2 = dataOut[0]->get();
      combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs, RooFit::Index(sam), RooFit::Import(sm[0].Data(),*dataOut[0]));
      if ( debug == true )
      {
        std::cout<<"[INFO] Adding: "<<dataOut[0]->GetName()<<" to combData"<<std::endl;
      }

      std::vector <RooDataSet*> combDataTmp;
      for( unsigned int i=1; i<sm.size(); i++ )
      {
        //std::cout<<"sm: "<<sm[i]<<std::endl; 
        TString dataNameComb2 = Form("combData%d",i);
        TString nD = dataOut[i]->GetName();
        if ( debug == true ) 
	      {
          std::cout<<"[INFO] Adding: "<<nD<<" to combData"<<std::endl;
	      }
        obs->Print(); 
        combDataTmp.push_back(new RooDataSet(dataNameComb2.Data(),dataNameComb2.Data(),*obs, RooFit::Index(sam), RooFit::Import(sm[i].Data(),*dataOut[i])));
        combData->append(*combDataTmp[i-1]);
      }
    }
    else
    {
      for (unsigned int i=0; i<sm.size(); i++ )
      {
        sam.defineType(sm[i].Data());
        std::cout<<"[INFO] Sample mode year hypo: "<<sm[i]<<std::endl; 
      }
      //const RooArgSet* obs2 = data[0]->get();
      combData = new RooDataSet(dataName.Data(),dataName.Data(),*obs, RooFit::Index(sam), RooFit::Import(sm[0].Data(),*data[0]));
      if ( debug == true )
      {
        std::cout<<"[INFO] Adding: "<<data[0]->GetName()<<" to combData"<<std::endl;
      }
      std::vector <RooDataSet*> combDataTmp;
      for( unsigned int i=1; i<sm.size(); i++ )
      {
        std::cout<<"[INFO] smp: "<<sm[i]<<" i:"<<i<<" size: "<<sm.size()<<std::endl; 
        TString dataNameComb2 = Form("combData%d",i);
        combDataTmp.push_back(new RooDataSet(dataNameComb2.Data(),dataNameComb2.Data(),*obs, RooFit::Index(sam), RooFit::Import(sm[i].Data(),*data[i])));
        if ( debug == true )
	      {
          std::cout<<"[INFO] Adding: "<<data[i]->GetName()<<" to combData"<<std::endl;
	      }
        combData->append(*combDataTmp[i-1]);
      }
    }
    
    return combData;
  }
  
  /*
    std::vector <TString> GetSampleMode(TString& sample, TString& mode, TString merge, bool debug )
    {
    std::vector <TString> sm;
    std::vector <TString> s;
    std::vector <TString> m;
    
    if (debug == true ){ std::cout<<"[INFO] Sample "<<sample<<". Mode "<<mode<<std::endl; }
    if ( (merge == "pol" || merge == "both") && sample != "both") { std::cout<<"[ERROR] Option --merge pol only possible for --pol both"<<std::endl; return NULL; }

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
  */

  //RooDataSet* GetDataSetToys(RooWorkspace* work, RooArgSet* obs, RooCategory& sam,
  //			     TString &dat, TString & sample, TString& mode, TString& year, TString& hypo,
  //			     TString merge, bool debug )

  std::vector <TString> GetSampleModeYearHypo(TString& sample, TString& mode, TString& year, TString& hypo, TString merge, bool debug )
  {
    std::vector <TString> smyh;
    std::vector <TString> s;
    std::vector <TString> m;
    std::vector <TString> y;
    std::vector <TString> h;

    if (debug) std::cout<<"[INFO] ==> GeneralUtils::GetSampleModeYearHypo(...)" << std::endl;

    if (debug == true ){ std::cout<<"[INFO] Sample "<<sample<<". Mode "<<mode<<". Year "<<year<<". Hypo "<<hypo<<": Merge: "<<merge<<std::endl; }
    if ( (merge == "pol" || merge == "both") && sample != "both") { std::cout<<"[ERROR] Option --merge pol only possible for --pol both"<<std::endl; return smyh; }
    if ( (merge == "year" || merge == "both") && year != "run1") { std::cout<<"[ERROR] Option --merge year only possible for --year run1"<<std::endl; return smyh; }

    TString newmerge;

    if (!merge.Contains("already")) //usual case
    {  
      s =  GetSample(sample, debug);
      y =  GetYear(year, debug );
      newmerge = merge;
    }
    else // if "alreadyyear/pol/both", the samples are "already" merged in the workspace (take names as they are)
    {
      newmerge = merge.ReplaceAll("already","");
      
      if(newmerge == "both")
      {  
        s =  GetSample(sample, "", debug);
        y =  GetDataYear(year, "", debug);
      }
      else
      {
        std::cout << "[ERROR] ==> GeneralUtils::GetSampleModeYearHypo(...): sorry, " << merge << " case not handled (yet).";
        exit(-1);
      }
      
    }    

    m =  GetMode(mode, debug );
    h =  GetHypo(hypo, debug );
    

    //    if ( y[0] == "")
    //  {
    //    smy = GetSampleMode(sample, mode, merge, debug);
    //  }
    // else
    //  {
    if ( newmerge == "" )
	  {
	    for(unsigned int i=0; i<m.size(); i++ )
      {
        for(unsigned int j=0; j<s.size(); j++ )
        {
          for(unsigned int k=0; k<y.size(); k++ )
		      {
            for(unsigned int l=0; l<h.size(); l++ )
            { 
              if(m[i] != ""){
                if(h[l] != "") {smyh.push_back(s[j]+"_"+m[i]+"_"+y[k]+"_"+h[l]);}
                else {smyh.push_back(s[j]+"_"+m[i]+"_"+y[k]);}
              }
              else{
                if(h[l] != "") {smyh.push_back(s[j]+"_"+y[k]+"_"+h[l]);}
                else {smyh.push_back(s[j]+"_"+y[k]);}  
              }
              if ( debug == true ) { std::cout<<"[INFO] Sample mode year hypo: "<<smyh[smyh.size()-1]<<std::endl;}
            } 
		      }
        }
      }
	  }
    else if ( newmerge == "pol") 
    {
      TString s1 = "both";
      for (unsigned int i=0; i<m.size(); i++ )
      {
        for(unsigned int k = 0; k<y.size(); k++ )
        {
          for(unsigned int l=0; l<h.size(); l++ )
          {  
            if(m[i] != ""){
              if(h[l] != "") {smyh.push_back(s1+"_"+m[i]+"_"+y[k]+"_"+h[l]);}
              else {smyh.push_back(s1+"_"+m[i]+"_"+y[k]);}
            }
            else{
              if(h[l] != "") {smyh.push_back(s1+"_"+y[k]+"_"+h[l]); }
              else {smyh.push_back(s1+"_"+y[k]);} 
            }
            if ( debug == true ) { std::cout<<"[INFO] Sample mode year hypo: "<<smyh[smyh.size()-1]<<std::endl;}
          }
        }
      }
    }
    else if ( newmerge == "year" )
	  {
	    TString y1 = "run1"; 
	    for (unsigned int i=0; i<m.size(); i++ )
      {
        for(unsigned int j = 0; j<s.size(); j++ )
        {
          for(unsigned int l=0; l<h.size(); l++ )
          {
            if(m[i] != ""){
              if(h[l] != "") {smyh.push_back(s[j]+"_"+m[i]+"_"+y1+"_"+h[l]);}
              else {smyh.push_back(s[j]+"_"+m[i]+"_"+y1);}
            }
            else{
              if(h[l] != "") {smyh.push_back(s[j]+"_"+y1+"_"+h[l]);}
              else{smyh.push_back(s[j]+"_"+y1);}  
            }
            if ( debug == true ) { std::cout<<"[INFO] Sample mode year hypo: "<<smyh[smyh.size()-1]<<std::endl;}
          } 
        }
      }

	  }
    else if ( newmerge == "both" )
	  {
	    TString s1 = "both";
	    TString y1 = "run1";
	    for (unsigned int i=0; i<m.size(); i++ )
      {
        for(unsigned int l=0; l<h.size(); l++ )
        { 
          if(m[i] != ""){
            if(h[l] != "") {smyh.push_back(s1+"_"+m[i]+"_"+y1+"_"+h[l]);}
            else {smyh.push_back(s1+"_"+m[i]+"_"+y1);}
          }
          else{
            if(h[l] != "") {smyh.push_back(s1+"_"+y1+"_"+h[l]);}
            else{smyh.push_back(s1+"_"+y1);}
          }
          if ( debug == true ) { std::cout<<"[INFO] Sample mode year hypo: "<<smyh[smyh.size()-1]<<std::endl;}
        }   
      }
	  }

    return smyh;

  }

  std::vector <TString>  GetYear(TString& year, bool debug )
  {
    std::vector <TString> y;
    if ( year == "run1")  { y.push_back("2011"); y.push_back("2012"); }
    else { y.push_back(year); }

    return y;
  }

  std::vector<TString> GetDataYear(TString check, TString merge, bool debug)
  {
    std::vector<TString> year;
    if ( merge == "year" || merge == "both")
    {
      year.push_back("2011");
      year.push_back("2012");
    }
    else
    {
      year.push_back(CheckDataYear(check,debug));
    }
    return year;
  }


  std::vector <TString>  GetSample(TString& sample, bool debug )
  {
    std::vector <TString> s;
    if ( sample == "both")  { s.push_back("up"); s.push_back("down"); }
    else { s.push_back(sample); }

    return s;
  }

  std::vector <TString>  GetSample(TString sample, TString merge, bool debug )
  {  
    std::vector <TString> s; 
    if ( merge == "pol" || merge == "both")
    {
      s.push_back("up"); 
      s.push_back("down");
      if (debug)
      {
        std::cout << "[INFO] ==> GeneralUtils::GetSample(...): sample up, down " << std::endl;
      } 
    }
    else
    { 
      s.push_back(CheckPolarity(sample,debug));
    }
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

  std::vector <TString>  GetHypo(TString& hypo, bool debug )
  {
    /*std::vector <TString> h;
    if(hypo != ""){ h.push_back(hypo+TString("Hypo")); }
    else{ h.push_back(TString("")); }*/
    std::vector <TString> h;
    if(hypo == ""){ h.push_back(""); }
    else if(hypo.Contains("_"))
    {
      if(debug){std::cout<<"[INFO] GeneralUtils::GetHypo(..): Multiple hypothesys selected. Splitting string"<<std::endl;}
      h = SplitString(hypo, "_");
      for(unsigned int hyp=0; hyp<h.size(); ++hyp){
        h[hyp] = h[hyp]+TString("Hypo");
      }
    }
    else
    {
      h.push_back(hypo+TString("Hypo"));
    }    

    return h;
  }  

  /*
    std::vector <Int_t> GetEntriesCombData(RooWorkspace* work, 
    TString &dat, TString & sample, TString& mode,
    TString merge, bool debug )
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
    else
    {
    nE = nEntries; 
    }
   
    return nE; 

    }
  */
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
    TString polarity ="";
    TString Check = check;
    polarity = CheckPolarity(Check, debug);
    return polarity; 
    
  }  

  TString CheckPolarity(TString& check, bool debug)
  {
    TString polarity = "";
    if (check.Contains("MD") == true  || check.Contains("down") == true || check.Contains("dw") == true || check.Contains("Down") == true ||
        check.Contains("md") == true  || check.Contains("Dw") == true || check.Contains("Dn") == true )
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
    if ( debug == true) std::cout<<"[INFO] ==> GeneralUtils::CheckPolarity(...): "<<polarity<<std::endl;
    return polarity;
  }

  TString CheckPolarityCapital(TString& check, bool debug)
  {
    TString pol = CheckPolarity(check,debug);
    if ( pol == "down" ) { return "Down"; }
    else if ( pol == "up" ) { return "Up"; }
    else if ( pol == "both" ) { return "Both"; } 

    return pol; 
  }

  std::vector<TString> GetPolarity(TString check, TString merge, bool debug)
  {
    std::vector<TString> pol;
    if ( merge == "pol" || merge == "both" )
    {
      pol.push_back("down");
      pol.push_back("up"); 
    }
    else
    {
      pol.push_back(CheckPolarity(check,debug));
    }
    return pol; 
  }
  
  //===========================================================================
  // Check D/Ds final state (kkpi,kpipi,pipipi) from check
  //==========================================================================
  TString CheckDMode(std::string& check, bool debug)
  {
    TString dmode = "";
    TString Check = check;
    dmode = CheckDMode(Check, debug);
    return dmode; 
  }

  TString CheckDMode(TString& check, bool debug)
  {
    TString dmode;
    if (check.Contains("KKpi") == true  || check.Contains("KKPi") == true || check.Contains("kkpi") == true )
    {
      dmode = "kkpi";
    }
    else if ( (check.Contains("Kpi") == true || check.Contains("KPi") == true || check.Contains("kpi") == true) &&
              ( check.Contains("Kpipi") == false && check.Contains("KPiPi") == false && check.Contains("kpipi") == false) )
    {
      dmode = "kpi";
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

  //==========================================================================                                                                                                          
  // Check KKPi final state (nonres,phipi,kstk) from check                                                                                    
  //==========================================================================

  TString CheckKKPiMode(std::string& check, bool debug)
  {
    TString dmode = "";
    TString Check = check;
    dmode = CheckKKPiMode(Check, debug);
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
    else if ( check.Contains("kkpi") == true || check.Contains("KKPi") == true )
    {
      kkpimode = "kkpi"; 
    }
    else
    {
      kkpimode = "";
    }
    if ( debug == true) std::cout<<"[INFO] Sample: "<<kkpimode<<std::endl;
    return kkpimode;
  }

  //==========================================================================                                                                                              
  // Check MC background decay                                                                                                                      
  //==========================================================================                      

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
    else if ( check.find("Bu") != std::string::npos || check.find("bu") != std::string::npos)
    { Bs="Bu"; } 
    else { Bs="Comb";}

    if (check.find("Lc") != std::string::npos ||
        check.find("lambdac") != std::string::npos ||
        check.find("Lambdac") != std::string::npos) { Ds = "Lc";}
    else if (check.find("Dsst") != std::string::npos || check.find("dsst") != std::string::npos)
    { Ds ="Dsst";}
    else if (check.find("Dst0") != std::string::npos || check.find("dst0") != std::string::npos)
    {Ds = "Dst0";}
    else if ( (check.find("Dst") != std::string::npos || check.find("dst") != std::string::npos) &&
              (check.find("Dst0") == std::string::npos || check.find("dst0") == std::string::npos))
    {Ds = "Dst";}
    else if ( (check.find("Ds") != std::string::npos  || check.find("ds") != std::string::npos) && 
              (check.find("Dsst") == std::string::npos || check.find("dsst") == std::string::npos ) &&
              (check.find("Dst") == std::string::npos || check.find("dst") == std::string::npos) &&
              (check.find("Dst0") == std::string::npos || check.find("dst0") == std::string::npos))
    { Ds = "Ds";}
    else if ( check.find("D0") != std::string::npos  || check.find("d0") != std::string::npos )
    { Ds = "D0";}
    else if (( check.find("D") != std::string::npos  || check.find("d") != std::string::npos )  &&
             ( check.find("D0") == std::string::npos  || check.find("d0") == std::string::npos ) &&
             (check.find("Ds") == std::string::npos  || check.find("ds") == std::string::npos) && check.find("ambda") == std::string::npos) 
    {Ds = "D";}
    else { Ds ="bkg";}

    if ( check.find("PiPi") != std::string::npos || check.find("pipi") != std::string::npos) { Bach = "PiPi"; }
    else if ( check.find("KPi") != std::string::npos || check.find("kpi") != std::string::npos) { Bach = "KPi"; }
    else if ( ( check.find("Pi") != std::string::npos || check.find("pi") != std::string::npos) &&
              ( check.find("PiPi") == std::string::npos || check.find("pipi") == std::string::npos) &&
              ( check.find("KPi") == std::string::npos || check.find("kpi") == std::string::npos) )
    { Bach = "Pi"; }
    else if( ( check.find("P") != std::string::npos || check.find("p") != std::string::npos ) && 
             ( check.find("Pi") == std::string::npos || check.find("pi") == std::string::npos) &&
             ( check.find("PiPi") == std::string::npos || check.find("pipi") == std::string::npos) &&
             ( check.find("KPi") == std::string::npos || check.find("kpi") == std::string::npos))
    {Bach = "p";}
    else if( (check.find("K") != std::string::npos || check.find("k") != std::string::npos )&& 
             (check.find("Kst") == std::string::npos || check.find("kst") == std::string::npos) &&
             ( check.find("KPi") == std::string::npos || check.find("kpi") == std::string::npos))
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

  //==========================================================================
  // Check bachelor mass hypothesys (k, pi) from check 
  //==========================================================================

  TString CheckHypo(std::string& check, bool debug)
  {
    TString hypo = "";
    TString Check = check;
    hypo = CheckHypo(Check, debug);
    return hypo;
  }

  TString CheckHypo(TString& check, bool debug)
  {
    TString hypo = "";
    if(check.Contains("DPiHypo") || check.Contains("DpiHypo")) { hypo = "Bd2DPiHypo"; }
    else if(check.Contains("DKHypo") || check.Contains("DkHypo")) { hypo = "Bd2DKHypo"; }
    else if(check.Contains("DsPiHypo") || check.Contains("DspiHypo")) { hypo = "Bs2DsPiHypo"; }
    else if(check.Contains("DsKHypo") || check.Contains("DskHypo")) { hypo = "Bs2DsKHypo"; }
    else if(check.Contains("D0PiHypo") || check.Contains("D0piHypo")){ hypo = "Bu2D0PiHypo";}    
    else if(check.Contains("D0KHypo") || check.Contains("D0kHypo")) {hypo = "Bu2D0KHypo";}    

    if ( debug == true) std::cout<<"[INFO] Hypo: "<<hypo<<std::endl;
    return hypo;
  }
  
  //==========================================================================                                                                                                    
  // Get decay in Latex                                                                                                                                                            
  //==========================================================================          

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
    else if (mode.Contains("Dst") == true || mode.Contains("dst") == true) {Ds ="D^{*}";}
    else if ( (mode.Contains("Ds") == true  || mode.Contains("ds") == true) && (mode.Contains("Dsst") != true || mode.Contains("dsst") != true ) &&
              ( mode.Contains("Dst") != true || mode.Contains("dst") != true )) { Ds = "D_{s}";}
    else if ((mode.Contains("D")==true || mode.Contains("d") == true )  &&  
             ( mode.Contains("Ds") != true || mode.Contains("ds") == true )) {Ds = "D";}
    else { Ds ="bkg";}

    if ( mode.Contains("Pi_") == true || mode.Contains("pi_") == true ) { Bach = "#pi"; }
    else if( (mode.Contains("p_") == true || mode.Contains("P_") == true ) && (mode.Contains("pi_") == true || mode.Contains("Pi_") == true )) 
    {Bach = "p";}
    else if( (mode.Contains("K_") == true || mode.Contains("k_") == true )&& (mode.Contains("Kst_")!=true || mode.Contains("kst_") != true) ) 
    {Bach = "K";}
    else if( ( mode.Contains("Kst_") == true || mode.Contains("kst_") == true ) ) {Bach ="K^{*}";}
    else if( mode.Contains("Rho_") == true || mode.Contains("rho_") == true ) {Bach = "#rho";}
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

  //==========================================================================                                                                                                             
  // Get Ds mode in capital letters                                                                                                                                                        
  //==========================================================================                                                                                                            
  TString GetModeCapital(TString& check, bool debug)
  {
    TString cap = check.Data();
    if ( check.Contains("kkpi") == true ) { cap = "KKPi"; }
    else if (check.Contains("kpipi") == true ) { cap = "KPiPi"; }
    else if (check.Contains("pipipi") == true ) { cap = "PiPiPi"; }
    else if (check.Contains("nonres") == true ) { cap = "NonRes"; }
    else if (check.Contains("phipi") == true) { cap = "PhiPi"; }
    else if (check.Contains("kstk") == true) { cap = "KstK"; }
    else if (check.Contains("hhhpi0") == true) { cap = "HHHPi0"; }
    
    return cap; 

  }

  //==========================================================================
  // Get Ds mode in lower letters                                                                                                                                                            
  //==========================================================================
  TString GetModeLower(TString& check, bool debug)
  { 

    TString low = check.Data(); 
    if ( check.Contains("kkpi") == true || check.Contains("KKPi") == true) {low = "kkpi";}
    else if (check.Contains("kpipi") == true || check.Contains("KPiPi") == true ) {low = "kpipi";}
    else if (check.Contains("pipipi") == true || check.Contains("PiPiPi") == true) {low = "pipipi";}
    else if (check.Contains("nonres") == true || check.Contains("NonRes") == true) {low = "nonres";}
    else if (check.Contains("phipi") == true || check.Contains("PhiPi") == true) {low = "phipi";}
    else if (check.Contains("kstk") == true || check.Contains("KstK") == true) {low = "kstk";}
    else if (check.Contains("hhhpi0") == true || check.Contains("HHHPi0") == true) {low = "hhhpi0";}
    
    return low; 
  }


  //=========================================================================
  // Check BDTG bin                                                                                                                                                           
  //=========================================================================

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

  //========================================================================== 
  // Check x axis description for observables   
  //==========================================================================   

  TString CheckObservable(TString& check, bool debug)
  {
    TString label = "";
    if( check.Contains("lab0_MassFitConsD_M") == true || check.Contains("lab0_MM") == true  ||
        (check.Contains("Bs") == true && check.Contains("Mass") == true) ||
	check.Contains("BeautyMass") == true ) { label = "Beauty Meson invariant mass [MeV/c^{2}]"; }
    else if ( check.Contains("Ds_MM") == true || check.Contains("lab2_MM") == true || check.Contains("CharmMass") == true ) { label = "Charm meson invariant mass [MeV/c^{2}]";}
    else if ( check.Contains("TAGDECISION") == true || check.Contains("DEC") == true || check.Contains("TagDec") == true ) 
    { 
      if ( check.Contains("SS_nnetKaon") == true || check.Contains("TagDecSS") == true )  { label = "tagging decision SS"; }
      else if ( check.Contains("TAGDECISION_OS") == true || check.Contains("TagDecSS") )  { label = "tagging decision OS"; }
      else { label = "tagging decision"; }
    }
    else if ( check.Contains("TAGOMEGA") == true || check.Contains("PROB") == true || check.Contains("Mistag") == true ) 
    {
      if ( check.Contains("SS_nnetKaon") == true || check.Contains("MistagSS") == true )  { label = "#omega SS"; }
      else if( check.Contains("TAGOMEGA_OS") == true || check.Contains("MistagOS") == true )  { label = "#omega OS"; }
      else { label = "#omega"; }
    }
    else if ( check.Contains("BeautyTimeErr") == true ) {label = "#sigma_{t} [ps]"; }
    else if ( check.Contains("LifetimeFit_ctau") == true || check.Contains("TAU") == true ||  
	      check.Contains("TRUETAU") == true  || check.Contains("BeautyTime") == true ) 
    {label ="t [ps]"; }
    else if ( check.Contains("BacCharge") == true || check.Contains("ID") == true && check.Contains("PIDK") == false && 
              ( check.Contains("lab1") == true || check.Contains("Bac") ==true) ) {label ="bachelor ID [1]"; }
    else if ( check.Contains("PIDK") == true && ( check.Contains("lab1") == true || check.Contains("Bac") ==true) ) {label ="bachelor log(|PIDK|)"; }
    else if ( check.Contains("_PT") == true || check.Contains("BacPT") == true) {label ="log(p_{t}) [MeV/c]"; }
    else if ( check.Contains("_P") == true && check.Contains("_PT") == false || check.Contains("BacP") == true) {label ="log(p) [MeV/c]"; }
    else if ( check.Contains("nTracks") == true ) {label ="log(nTracks)"; }
    else if ( check.Contains("BDTG") == true ) { label = "BDTG classifier"; }
    else { label = check; } 
    
    if ( debug == true) std::cout<<"[INFO] Observable label: "<<label<<std::endl;

    return label;
  }

  //==========================================================================    
  // Check bachelor particle
  //==========================================================================    
            
  TString CheckBachelor(TString check, bool debug)
  {
    TString bachelor = "";
    
    if( check.Contains("CombPi") == true ) { TString s1 = "CombPi"; TString s2 = ""; check.ReplaceAll(s1,s2); }
    if( check.Contains("CombK") == true ) { TString s1 = "CombK"; TString s2 = ""; check.ReplaceAll(s1,s2); }
    if( check.Contains("MC Bs2DsK") == true ) { TString s1 = "Bs2DsK"; TString s2 = ""; check.ReplaceAll(s1,s2); }
    if( check.Contains("MC Bs2DsPi") == true ) { TString s1 = "Bs2DsPi"; TString s2 = ""; check.ReplaceAll(s1,s2); }
 
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

  TString CheckBachelorLong(TString check, bool debug)
  {
    TString bachelor = "";

    if( check.Contains("CombPi") == true ) { TString s1 = "CombPi"; TString s2 = ""; check.ReplaceAll(s1,s2); }
    if( check.Contains("CombK") == true ) { TString s1 = "CombK"; TString s2 = ""; check.ReplaceAll(s1,s2); }
    if( check.Contains("MC Bs2DsK") == true ) { TString s1 = "Bs2DsK"; TString s2 = ""; check.ReplaceAll(s1,s2); }
    if( check.Contains("MC Bs2DsPi") == true ) { TString s1 = "Bs2DsPi"; TString s2 = ""; check.ReplaceAll(s1,s2); }

    if( check.Contains("pion") == true || check.Contains("Pion") == true )

    {
      bachelor = "Pion";
    }
    else if ( check.Contains("kaon") == true || check.Contains("Kaon") == true)

    {
      bachelor = "Kaon";
    }
    else if ( check.Contains("proton") == true || check.Contains("Proton") == true )
    {
      bachelor = "Proton";
    }

    if ( debug == true) std::cout<<"[INFO] Sample: "<<bachelor<<std::endl;

    return bachelor;
  }
  //========================================================================== 
  // Check Stripping number                    
  //==========================================================================                
 
  TString CheckStripping(TString& check, bool debug)
  {
    TString str="";
    if( check.Contains("Str17") == true || check.Contains("str17") == true || check.Contains("Stripping17") == true || check.Contains("stripping17") == true )
    {
      str = "str17"; 
    }
    else if ( check.Contains("Str20r1") == true|| check.Contains("str20r1") == true || check.Contains("Stripping20r1") == true || check.Contains("stripping20r1") ==true )
    {
      str = "str20r1";
    }
    else if ( check.Contains("Str20") == true|| check.Contains("str20") == true || check.Contains("Stripping20") == true || check.Contains("stripping20") ==true )
    {
      str = "str20";
    }
    else if ( check.Contains("Str21r1") == true|| check.Contains("str21r1") == true || check.Contains("Stripping21r1") == true || check.Contains("stripping21r1") ==true )
    {
      str = "str20r1";
    }
    else if ( check.Contains("Str21") == true|| check.Contains("str21") == true || check.Contains("Stripping21") == true || check.Contains("stripping21") ==true )
    {
      str = "str21";
    }
    if (debug == true ){ std::cout<<"[INFO] Check Stripping: "<<str<<std::endl; } 

    return str; 
  }

  TString CheckStripping(std::string& check, bool debug)
  {
    std::string str = "";
    TString Check = check;
    TString Str = "";
    Str = CheckStripping(Check, debug);
    str = Str;
    return str; 
  }

  TString CheckStrippingNumber(TString& check, bool debug)
  {
    TString str="";
    if( check.Contains("Str17") == true || check.Contains("str17") == true || check.Contains("Stripping17") == true || check.Contains("stripping17") == true )
    {
      str = "17";
    }
    else if ( check.Contains("Str20r1") == true|| check.Contains("str20r1") == true || check.Contains("Stripping20r1") == true || check.Contains("stripping20r1") ==true )
    {
      str = "20r1";
    }
    else if ( check.Contains("Str20") == true|| check.Contains("str20") == true || check.Contains("Stripping20") == true || check.Contains("stripping20") ==true )
    {
      str = "20";
    }
    else if ( check.Contains("Str21r1") == true|| check.Contains("str21r1") == true || check.Contains("Stripping21r1") == true || check.Contains("stripping21r1") ==true )
    {
      str = "21r1";
    }
    else if ( check.Contains("Str21") == true|| check.Contains("str21") == true || check.Contains("Stripping21") == true || check.Contains("stripping21") ==true )
    {
      str = "21";
    }
    if (debug == true ){ std::cout<<"[INFO] Check Stripping: "<<str<<std::endl; }

    return str;
  }


  TString CheckStrippingNumber(std::string& check, bool debug)
  {
    std::string str = "";
    TString Check = check;
    TString Str = "";
    Str = CheckStrippingNumber(Check, debug);
    str = Str;
    return str;
  }

  //==========================================================================    
  // Check data year                                                                 
  //==========================================================================                
 
  TString CheckDataYear(TString& check, bool debug)
  {
    TString year = "";
    if (check.Contains("2011") == true)
    { year ="2011"; }
    else if (check.Contains("2012") == true )
    { year = "2012";}
    else if (check.Contains("run1") == true || check.Contains("Run1") == true )
    { year = "run1"; } 
    if (debug == true ){ std::cout<<"[INFO] Check data year: "<<year<<std::endl; }
    return year;    
  }

  TString CheckDataYear(std::string& check, bool debug)
  {
    std::string year = "";
    TString Check = check;
    TString Year = CheckDataYear(Check, debug);
    year = Year;
    return year;
  }
  
  //==========================================================================                                                                                                                      
  // Get X label for plotting                                                                                                                                                                       
  //==========================================================================                                                                                                                      
  TString GetXLabel(TString decay, TString var, TString mode, bool debug )
  {
    TString label = ""; 
    
    TString happystar = "#lower[-0.95]{#scale[0.5]{(}}#lower[-0.8]{#scale[0.5]{*}}#lower[-0.95]{#scale[0.5]{)}}";
    TString happystar2 = "#lower[-0.65]{#scale[0.6]{*}}";
    TString happypm   = "#lower[-0.95]{#scale[0.6]{#pm}}";
    TString happymp   = "#lower[-0.95]{#scale[0.6]{#mp}}";
    TString happystarpm = "#lower[-0.95]{#scale[0.6]{*#pm}}";
    TString happyplus = "#lower[-0.95]{#scale[0.6]{+}}";
    TString happymin  = "#lower[-1.15]{#scale[0.7]{-}}";
    TString happy0   = "#lower[-0.85]{#scale[0.6]{0}}";

    if (var.Contains("PIDK") == true)
    {
      if ( decay.Contains("Pi") == true )
      {
        label = "#font[132]{Companion ln(|L(#pi#kern[0.1]{/#kern[0.1]{K}})|)}";
      }
      else 
      {
        label = "#font[132]{Companion ln(|L(K#kern[0.1]{/#kern[0.1]{#pi}})|)}";
      }
    }
    else if ( var.Contains("lab2") == true  ||  var.Contains("Ds_MM") == true  ||  var.Contains("CharmMass") == true)
    {
      if ( mode == "all") 
      {
        label = "#font[132]{m(K^{+}K^{-}#pi^{#pm}, #pi^{+}#pi^{-}#pi^{#pm}, K^{#pm}#pi^{-}#pi^{+}) [MeV/#font[12]{c}^{2}]}";
      }
      else if (  mode == "nonres" || mode == "kstk" || mode== "phipi" || mode == "kkpi")
      {
        label = "#font[132]{m(K^{+}K^{-}#pi^{#pm}) [MeV/#font[12]{c}^{2}]}";
      }
      else if (mode == "kpipi") 
      {
        label = "#font[132]{m(K^{#pm}#pi^{-}#pi^{+}) [MeV/#font[12]{c}^{2}]}";
      }
      else if (  mode == "pipipi") 
      {
        label = "#font[132]{m(#pi^{+}#pi^{-}#pi^{#pm}) [MeV/#font[12]{c}^{2}]}";
      }
      else if (  mode == "hhhpi0" )
      {
        label = "#font[132]{m(K^{+}K^{-}#pi^{#pm}#pi^{0}) [MeV/#font[12]{c}^{2}]}";
      }
      else
      {
        std::cout<<"[ERROR] Wrong charm mode: "<<mode<<std::endl;
        return label; 
      }
    }
    else
    {
      if ( decay.Contains("DsstPi") == true )
      {
        if ( decay.Contains("DsstPi") == true )
        {
          label = "#font[132]{m(D_{s}#kern[-0.3]{"+happystar2+happymin+"}#kern[0.1]{#pi#lower[-0.95]{#scale[0.6]{+}}}) [MeV/#font[12]{c}^{2}]}";
        }
        else if ( decay.Contains("DsstK") == true ) 
        {
          label = "#font[132]{m(D_{s}#kern[-0.3]{"+happystar2+happymp+"}#kern[0.1]{K"+happypm+"}) [MeV/#font[12]{c}^{2}]}";
        }
        else if ( decay.Contains("DsPi") == true )
        {
          label = "#font[132]{m(D_{s}#kern[-0.3]{"+happymin+"}#kern[0.1]{#pi#lower[-0.95]{#scale[0.6]{+}}}) [MeV/#font[12]{c}^{2}]}";
        }
        else if ( decay.Contains("DsK") == true )
        {
          label = "#font[132]{m(D_{s}#kern[-0.3]{"+happymp+"}#kern[0.1]{K"+happypm+"}) [MeV/#font[12]{c}^{2}]}";
        }
        else if ( decay.Contains("DPi") == true )
        {
          label = "#font[132]{m(D#kern[-0.3]{"+happymin+"}#kern[0.1]{#pi#lower[-0.95]{#scale[0.6]{+}}}) [MeV/#font[12]{c}^{2}]}";
        }
        else if ( decay.Contains("LcPi") == true )
        {
          label = "#font[132]{m(#Lambda_{c}#kern[-0.3]{"+happymin+"}#kern[0.1]{#pi#lower[-0.95]{#scale[0.6]{+}}}) [MeV/#font[12]{c}^{2}]}";
        }
	else
	  {
	    std::cout<<"[ERROR] Wrong charm decay: "<<decay<<std::endl;
	    return label;
	  }
      }
      else if ( decay.Contains("DsstK") == true ) 
      {
        label = "#font[132]{m(D_{s}#kern[-0.3]{"+happystar2+happymp+"}#kern[0.1]{K"+happypm+"}) [MeV/#font[12]{c}^{2}]}";
      }
      else if ( decay.Contains("DsPi") == true )
      {
        label = "#font[132]{m(D_{s}#kern[-0.3]{"+happymin+"}#kern[0.1]{#pi#lower[-0.95]{#scale[0.6]{+}}}) [MeV/#font[12]{c}^{2}]}";
      }
      else if ( decay.Contains("DsK") == true )
      {
        label = "#font[132]{m(D_{s}#kern[-0.3]{"+happymp+"}#kern[0.1]{K"+happypm+"}) [MeV/#font[12]{c}^{2}]}";
      }
      else if ( decay.Contains("DPi") == true )
      {
        label = "#font[132]{m(D#kern[-0.3]{"+happymin+"}#kern[0.1]{#pi#lower[-0.95]{#scale[0.6]{+}}}) [MeV/#font[12]{c}^{2}]}";
      }
      else if ( decay.Contains("LcPi") == true )
        {
          label = "#font[132]{m(#Lambda_{c}#kern[-0.3]{"+happymin+"}#kern[0.1]{#pi#lower[-0.95]{#scale[0.6]{+}}}) [MeV/#font[12]{c}^{2}]}";
        }

      else
      {
        std::cout<<"[ERROR] Wrong charm decay: "<<decay<<std::endl;
        return label;
      }
    }
    return label; 
  }

  TString GetXLabel(std::string& decay, std::string& var, std::string& mode, bool debug)
  {
    TString Decay = decay;
    TString Var = var; 
    TString Mode = mode; 
    TString Label = GetXLabel(Decay, Var, Mode, debug);
    return Label;
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

  std::vector <TString> SplitString(TString string, TString pattern)
  {
    TObjArray *tlist = string.Tokenize(pattern.Data());
    Int_t nstrings = tlist->GetEntries();
    std::vector <TString> list;
    list.reserve(nstrings);
    for (Int_t i = 0; i < nstrings; ++i)
    {
      list.push_back( ((TObjString *)(tlist->At(i)))->String() );
    }
    
    return list;
  }  

  std::vector <TString> GetList(TString name, TString name2 , TString name3)
  {
    std::vector <TString> list;
    list.push_back(name);
    if ( name2 != "" ) { list.push_back(name2); }
    if ( name3 != "" ) { list.push_back(name3); }
    
    return list; 
  }


  std::vector <TString> AddToList(std::vector <TString> list, TString name)
  {
    list.push_back(name);
    return list; 
  }

  
  std::vector < std::vector <TString> > GetList2D(TString name, TString name2)
  {
    std::vector< std::vector < TString > > matrix;
    std::vector<TString> myvector;
    myvector.push_back(name);
    myvector.push_back(name2); 
    matrix.push_back(myvector);
    
    return matrix; 
  }

  std::vector < std::vector <TString> > AddToList2D(std::vector < std::vector <TString> > matrix, TString name,TString name2)
  {
    std::vector<TString> myvector;
    myvector.push_back(name);
    myvector.push_back(name2);
    matrix.push_back(myvector);
    return matrix; 
    
  }

  void printList2D(std::vector < std::vector <TString> > matrix)
  {
    for(unsigned int i = 0; i < matrix.size(); i ++ )
    {
      for (unsigned int j = 0; j < matrix[i].size(); j ++ )
      {
        std::cout<<"element: "<<i<<" "<<j<<" : "<<matrix[i][j]<<std::endl; 
      }
    }
  }
  
  std::pair <TString, TString> GetNameExpectedYields(TString mode,  bool debug)
  {
    TString Mode ="";
    if(mode.Contains("DPi") ){ Mode = "Bd2DPi"; }
    else if ( mode.Contains("LcPi")) { Mode = "Lb2LcPi"; }
    else if ( mode.Contains("DsPi")) { Mode = "Bs2DsPi"; }
    else if ( mode.Contains("DsK")) { Mode = "Bs2DsK"; }
    else if ( mode.Contains("DK")) { Mode = "Bd2DK"; }
    else if ( mode.Contains("DsstK")) { Mode = "Bs2Ds*K"; } 
    else if ( mode.Contains("DsstPi")) { Mode = "Bs2Ds*Pi"; } 
    else if ( mode.Contains("Dsp")) { Mode = "Lb2Dsp";} 
    else if ( mode.Contains("Dsstp")) { Mode = "Lb2Dsstp";} 
    else if ( mode.Contains("LcK")) { Mode = "Lb2LcK"; } 
    else { Mode = mode; }

    TString ModeD = "";
    if (mode.Contains("DPi") || mode.Contains("DK")) { ModeD = "kpipi"; }
    else if ( mode.Contains("Lc") ) { ModeD = "pkpi"; }
    else {
      ModeD =  CheckDMode(mode, debug);
      if ( ModeD == "kkpi" || ModeD == ""){ ModeD = CheckKKPiMode(mode, debug);}
    }
    std::pair <TString,TString> hypo(Mode,ModeD); 
    if (debug == true ) { std::cout<<"[INFO] Hypothesis name: "<<hypo.first<<" , "<<hypo.second<<std::endl; }
    return hypo; 
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
