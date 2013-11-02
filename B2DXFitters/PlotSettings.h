/*****************************************************************************
 * Project: RooFit                                                           *
 * Description: class contains plot settings for MDFitter                    *
 *                                                                           * 
 * author: Agnieszka Dziurda  * agnieszka.dziurda@cern.ch                    *
 *                                                                           *
 *****************************************************************************/

#ifndef PLOTSETTINGS
#define PLOTSETTINGS

#include "Riostream.h"
#include "TString.h"
#include "TNamed.h"
 
#include <vector>

class PlotSettings : public TNamed {

public:
  PlotSettings(){};
  PlotSettings(const TString& name, const TString& title);
  PlotSettings(const TString& name, const TString& title, TString dir, TString ext, Int_t bin, Bool_t save, Bool_t log, Bool_t titlestatus);
  
  PlotSettings(const TString& name, const TString& title, 
	       TString dir, TString ext, Int_t bin, Bool_t save, Bool_t log, Bool_t titlestatus,
	       std::vector <Color_t> colorData, std::vector <Color_t> colorPdf, std::vector <Style_t> stylePdf);
  
  PlotSettings(const PlotSettings& other);
  virtual TObject* clone() const { return new PlotSettings(*this); }

  friend std::ostream & operator<< (std::ostream &out, const PlotSettings &s);
  virtual ~PlotSettings();

  void SetDir(TString dir)   { _dir = dir; }
  void SetExt(TString ext)   { _ext = ext; }
  void SetBin(Int_t bin)     { _bin = bin; }
  void SetStatus(Bool_t save ) { _save = save; }
  void SetLogStatus(Bool_t log) { _log = log; }
  void SetTitleStatus(Bool_t title) { _title = title; }

  void SetColorData( std::vector <Color_t> colorData ) { _colorData = colorData; }
  void SetColorPdf( std::vector <Color_t> colorPdf ) { _colorPdf = colorPdf; }
  void SetStylePdf( std::vector <Style_t> stylePdf ) { _stylePdf = stylePdf; }

  void SetColorData( Color_t color, Int_t i ) { _colorData[i] = color; }
  void SetColorPdf(  Color_t color, Int_t i ) { _colorPdf[i] = color; }
  void SetStylePdf(  Style_t style, Int_t i ) { _stylePdf[i] = style ; }

  void AddColorData( Color_t color ) { _colorData.push_back(color); }
  void AddColorPdf(  Color_t color ) { _colorPdf.push_back(color); }
  void AddStylePdf(  Style_t style ) { _stylePdf.push_back(style); }

  Int_t GetSizeColorData() { return _colorData.size(); }
  Int_t GetSizeColorPdf() { return _colorPdf.size(); }
  Int_t GetSizeStylePdf() { return _stylePdf.size(); }
  
  Color_t GetColorData(Int_t i) { return _colorData[i]; }
  Color_t GetColorPdf(Int_t i) { return _colorPdf[i];}
  Color_t GetStylePdf(Int_t i) { return _stylePdf[i];}

  TString GetDir() { return _dir; }
  TString GetExt() { return _ext; }
  Int_t   GetBin() { return _bin; }
  Bool_t  GetStatus() { return _save; }
  Bool_t  GetLogStatus() { return _log; }
  Bool_t  GetTitleStatus() { return _title; }

  virtual void Print(Option_t * /*option*/ = "") const { std::cout<<*this<<std::endl;}

protected:

  TString _dir;
  TString _ext;
  Int_t _bin;
  Bool_t _save;
  Bool_t _log;
  Bool_t _title;
  std::vector <Color_t> _colorData;
  std::vector <Color_t> _colorPdf;
  std::vector <Style_t> _stylePdf;
    
private:
  ClassDef(PlotSettings, 1);
};
 
#endif
