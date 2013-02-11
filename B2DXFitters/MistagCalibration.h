/**
 * @file MistagCalibration.cxx
 *
 * Mistag calibration with polynomial
 *
 * @author Vladimir Gligorov <vladimir.gligorov@cern.ch>
 * @date 2012-09-11
 * 	initial version
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-10-09
 * 	subsequent cleanups, functionality for calibration polynomials,
 * 	integrals over mistag
 */
#ifndef MISTAGCALIBRATION
#define MISTAGCALIBRATION

#include <RooAbsReal.h>
#include <RooRealProxy.h>
#include <RooListProxy.h>

/**
 * @brief Mistag calibration with polynomials
 *
 * calibrate with \f$ \eta_c=\sum_k p_k\cdot (\eta-\eta_{avg})^k \f$
 *
 * @author Vladimir Gligorov <vladimir.gligorov@cern.ch>
 * @date 2012-09-11
 * 	initial version
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-10-09
 * 	subsequent cleanups, functionality for calibration polynomials,
 * 	integrals over mistag
 */
class MistagCalibration : public RooAbsReal
{
    public:
	/// default constructor for ROOT I/O
	MistagCalibration() {};
	/// constructor to calibrate with eta_c = p0 + p1 * eta
	MistagCalibration(const char *name, const char *title,
		RooAbsReal& eta, RooAbsReal& p0, RooAbsReal& p1);
	/// constructor to calibrate with eta_c = p0 + p1*(eta-etaavg)
	MistagCalibration(const char *name, const char *title,
		RooAbsReal& eta, RooAbsReal& p0, RooAbsReal& p1,
		RooAbsReal& etaavg);
	/// constructor to calibrate with eta_c=sum_k p_k*(eta-etaavg)^k
	MistagCalibration(const char *name, const char *title,
		RooAbsReal& eta, RooArgList& calibcoeffs,
		RooAbsReal& etaavg);
	/// copy constructor
	MistagCalibration(const MistagCalibration& other, const char* name = 0);
	/// cloning operation
	virtual TObject* clone(const char* newname) const;
	/// destructor
	virtual ~MistagCalibration();

	/// announce capability to calculate analytical integrals
	Int_t getAnalyticalIntegral(
		RooArgSet& allVars, RooArgSet& anaIntVars,
		const char* rangeName) const;
	/// calculate analytical integrals
	Double_t analyticalIntegral(Int_t code, const char* rangeName) const;

    protected:
	/// return calibrated mistag
	Double_t evaluate() const;

    private:
	RooRealProxy m_eta;		///< predicted mistag
	RooListProxy m_calibcoeffs;	///< coefficients of calibration poly
	RooRealProxy m_etaavg;		///< average mistag

	/// common initialisation
	void init(const RooArgList& coeffs, RooAbsReal& eta);
	/// do the calculation for the mistag integral
	Double_t evalIntEta(
		const double etalo, const double etahi) const;

	ClassDef(MistagCalibration, 2);
};

#endif
