/**
 * @file FinalStateChargePdf.h
 *
 * pdf to describe final state charge distribution (in terms of an asymmetry)
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-10-16
 */
#ifndef FINALSTATECHARGEPDF
#define FINALSTATECHARGEPDF

#include <RooAbsReal.h>
#include <RooAbsPdf.h>
#include <RooAbsCategory.h>
#include <RooRealProxy.h>
#include <RooCategoryProxy.h>

/** @brief pdf to describe final state charge distribution
 *
 * pdf to describe final state charge distribution (in terms of an asymmetry)
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-10-16
 */
class FinalStateChargePdf : public RooAbsPdf
{
    public:
	/// default constructor for ROOT I/O
	FinalStateChargePdf() {}; 
	/// constructor
	FinalStateChargePdf(const char *name, const char *title,
		RooAbsCategory& qf, RooAbsReal& asymm);
	/// copy constructor
	FinalStateChargePdf(const FinalStateChargePdf& other, const char* name = 0);
	/// clone
	virtual TObject* clone(const char* newname) const;
	/// destructor
	virtual ~FinalStateChargePdf();

	/// anounce analytical integrals
	virtual Int_t getAnalyticalIntegral(
		RooArgSet& allVars, RooArgSet& anaIntVars,
		const char* rangeName = 0) const;
	/// provide analytical integrals
	virtual Double_t analyticalIntegral(
		Int_t code, const char* rangeName = 0) const;

    protected:
	RooCategoryProxy m_qf;		///< final state charge
	RooRealProxy m_asymm;		///< asymmetry

	Double_t evaluate() const;
	Double_t eval(const int qf) const;

   private:
	ClassDef(FinalStateChargePdf, 1);
};

#endif // FINALSTATECHARGEPDF

// vim: sw=4:tw=78:ft=cpp
