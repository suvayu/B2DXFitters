/*****************************************************************************
 * Project: RooFit                                                           *
 * Package: RooFitModels                                                     *
 *    File: $Id$
 * Authors:                                                                  *
 *   Manuel Schiller
 *                                                                           *
 *                                                                           *
 * Redistribution and use in source and binary forms,                        *
 * with or without modification, are permitted according to the terms        *
 * listed in LICENSE (http://roofit.sourceforge.net/license.txt)             *
 *****************************************************************************/
#ifndef ROOSWIMMINGACCEPTANCE_H
#define ROOSWIMMINGACCEPTANCE_H

#include <vector>
#include <utility>

#include "RooAbsGaussModelEfficiency.h"
#include "RooListProxy.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
class RooAbsReal;

class RooRealVar;
class RooArgList;
class TH1;

class RooSwimmingAcceptance : public RooAbsGaussModelEfficiency {
public:
    /// enum to characterise the state of the acceptance after the first TP
    enum InitialTurningPointState { Off = 0, On = 1 };
public:
    /// default constructor (for ROOT I/O)
    RooSwimmingAcceptance();
    /** @brief construct an acceptance from a series of turning points (TPs)
     * 
     * @param name                name of the acceptance
     * @param title               title of the acceptance
     * @param x                   observable
     * @param nTurningPoints      number of acceptance TPs in x
     * @param turningPoints       list of acceptance TPs in x 
     * @param initialTurningPoint state of first acceptance TP (On/Off)
     *
     * Given an observable x, an acceptance for use in swimming fits is
     * constructed from a category variable that specifies the number of
     * turning points (TPs) of a candidate, and a list of turning points.
     * Depending on initialTurningPoint, the first turning point is assumed
     * to turn the acceptance either On or Off. 
     */
    RooSwimmingAcceptance(const char* name, const char* title,
    RooRealVar& x, RooAbsCategory& nTurningPoints, const RooArgList& turningPoints,
    InitialTurningPointState initialTurningPoint = On);
    /// destructor
    ~RooSwimmingAcceptance();

    /// copy constructor, optionally setting a new name
    RooSwimmingAcceptance(const RooSwimmingAcceptance& other, const char* name = 0);
    /// clone method
    RooSwimmingAcceptance* clone(const char* newname) const { return new RooSwimmingAcceptance(*this, newname); }

    Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName) const;
    Double_t analyticalIntegral(Int_t code, const char* rangeName) const;

    Int_t getMaxVal(const RooArgSet& vars) const;
    Double_t maxVal(Int_t code) const;

    std::list<Double_t>* binBoundaries(RooAbsRealLValue& obs, Double_t xlo, Double_t xhi) const;

    // for use as RooAbsGaussModelEfficiency...
    std::complex<double> productAnalyticalIntegral(Double_t umin, Double_t umax, Double_t scale, Double_t offset, const std::complex<double>& z) const;

    //const RooArgList& coefficients() const { return _coefList; }

    // std::list<Double_t>* plotSamplingHint(RooAbsRealLValue& obs, Double_t xlo, Double_t xhi) const;

private:
    bool m_initialTPState;
    RooRealProxy m_x;
    RooCategoryProxy m_nTp;
    RooListProxy m_tpList;
    mutable std::vector<double> m_tps; //!
    mutable std::vector<RooGaussModelAcceptance::M_n<1U> > m_M; //!

    Double_t evaluate() const;
    /// update list of TP for current candidate
    // update list of turning points between min and max, return initial state
    bool updateTPs(double min = -std::numeric_limits<double>::max(),
                   double max = +std::numeric_limits<double>::max()) const;
    ClassDef(RooSwimmingAcceptance, 1) // swimming acceptance function
};

#endif
