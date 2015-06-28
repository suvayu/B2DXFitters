#include <cmath>
#include <cassert>
#include <iostream>
#include <algorithm>

#include "TRandom.h"
#include "TRandom3.h"
#include "TFile.h"
#include "Math/SVector.h"
#include "Math/CholeskyDecomp.h"

#include "TH1D.h"
#include "TF1.h"
#include "TPad.h"
#include "TStyle.h"
#include "TVirtualFitter.h"

#include "../B2DXFitters/TagCombiner.h"

enum { N = 2 };

typedef ROOT::Math::SVector<double, N> DLLVector;

/// calibration of a single tagger
class Calibration {
    private:
	static const double s_nan; ///< NaN

	double m_aveta; ///< average eta
	double m_calibparams[2]; ///< p0, p1
	double m_calibparamcov[3]; ///< covariance matrix (if you fit)

    public:
	/// default constructor
	Calibration() : m_aveta(s_nan)
        {
	    std::fill(m_calibparams, m_calibparams + 2, s_nan);
	    std::fill(m_calibparamcov, m_calibparamcov + 3, s_nan);
	}

	/// constructor
	Calibration(const double etaavg, const double p0, const double p1)
	{
	    m_aveta = etaavg;
	    m_calibparams[0] = p0;
	    m_calibparams[1] = p1;
	    std::fill(m_calibparamcov, m_calibparamcov + 3, s_nan);
	}

	/// constructor (with uncertainties/covariance)
	Calibration(const double etaavg, const double p0, const double p1,
		const double cov00, const double cov10, const double cov11)
	{
	    m_aveta = etaavg;
	    m_calibparams[0] = p0;
	    m_calibparams[1] = p1;
	    m_calibparamcov[0] = cov00;
	    m_calibparamcov[1] = cov10;
	    m_calibparamcov[2] = cov11;
	}

	/// perform an analytical straight line chi^2 fit to the given 1D histogram
	Calibration(const double etaavg, const TH1* hist) : m_aveta(etaavg)
	{
	    using TagTools::evalCalibPoly;
	    using ROOT::Math::CholeskyDecomp;
	    // initial parameter estimates
	    m_calibparams[0] = m_aveta;
	    m_calibparams[1] = 1.;

	    double tmp[5], *rhs = &tmp[3];
	    unsigned iter = 32;
	    do { 
		// zero matrix and right hand size
		std::fill(tmp, tmp + 5, 0.);
		// accumulate contributions of bins
		for (unsigned i = 1; i <= unsigned(hist->GetNbinsX()); ++i) {
		    const double e = hist->GetBinError(i);
		    // skip empty/invalid bins
		    if (e != e || e <= 0.) continue;
		    const double w = 1. / (e * e);
		    const double eta = hist->GetBinCenter(i);
		    const double deta = eta - m_aveta;
		    const double wdeta = w * deta;
		    const double domega = hist->GetBinContent(i) -
			evalCalibPoly(eta, m_aveta, m_calibparams);

		    tmp[0] += w;
		    tmp[1] += wdeta;
		    tmp[2] += wdeta * deta;
		    rhs[0] += w * domega;
		    rhs[1] += wdeta * domega;
		}
		// decompose matrix
		CholeskyDecomp<double, 2> decomp(tmp);
		// check for singular matrix
		if (!decomp) throw;
		// solve for parameter shifts
		decomp.Solve(rhs);
		// save covariance matrix
		decomp.Invert(m_calibparamcov);

		// update parameters with shifts
		m_calibparams[0] += rhs[0];
		m_calibparams[1] += rhs[1];

		// iterate fit until stable
	    } while ((std::abs(rhs[0]) > 1e-15 || std::abs(rhs[1]) > 1e-15) && (--iter));
	    // check for no convergence
	    if (!iter && (std::abs(rhs[0]) > 1e-15 || std::abs(rhs[1]) > 1e-15)) throw;
	}

	/// upward perturbation of calibration
	Calibration& operator+=(const Calibration& other)
	{
	    assert(other.m_aveta == m_aveta);
	    m_calibparams[0] += other.m_calibparams[0];
	    m_calibparams[1] += other.m_calibparams[1];
	    m_calibparamcov[0] += other.m_calibparamcov[0];
	    m_calibparamcov[1] += other.m_calibparamcov[1];
	    m_calibparamcov[2] += other.m_calibparamcov[2];
	    return *this;
	}

	/// downward perturbation of calibration
	Calibration& operator-=(const Calibration& other)
	{
	    assert(other.m_aveta == m_aveta);
	    m_calibparams[0] -= other.m_calibparams[0];
	    m_calibparams[1] -= other.m_calibparams[1];
	    m_calibparamcov[0] += other.m_calibparamcov[0];
	    m_calibparamcov[1] += other.m_calibparamcov[1];
	    m_calibparamcov[2] += other.m_calibparamcov[2];
	    return *this;
	}

	/// C++ stream output
	std::ostream& print(std::ostream& os) const
	{
	    std::ios::fmtflags oflags = os.flags();
	    os.setf(std::ios::fixed, std::ios::floatfield);
	    std::streamsize ow = os.width(), op = os.precision();

	    const double ep0 = std::sqrt(m_calibparamcov[0]);
	    const double ep1 = std::sqrt(m_calibparamcov[2]);
	    const double correl = m_calibparamcov[1] / (ep0 * ep1);

	    os << "eta_c = " << m_calibparams[0];
	    if (ep0 > 0.) os << "+/-" << ep0;
	    os << " + (" << m_calibparams[1];
	    if (ep1 > 0.) os << "+/-" << ep1;
	    os << ") * (eta - " << m_aveta << ")";
	    if (ep0 > 0. && ep1 > 0.) os << " --- correl(p0, p1) = " << correl;

	    os.flags(oflags);
	    os.width(ow);
	    os.precision(op);

	    return os;
	}

	/// return average eta
	double aveta() const { return m_aveta; }
	/// return calibration parameters
	const double (&calibparams() const)[2] { return m_calibparams; }
	/// return (packed) covariance matrix
	const double (&calibparamcov() const)[3] { return m_calibparamcov; }
};

const double Calibration::s_nan(std::numeric_limits<double>::quiet_NaN());

/// upward perturbation of calibration
Calibration operator+(const Calibration& a, const Calibration& b)
{ return Calibration(a) += b; }

/// downward perturbation of calibration
Calibration operator-(const Calibration& a, const Calibration& b)
{ return Calibration(a) -= b; }

/// unary minus (makes most sense to "flip" a delta between calibrations)
Calibration operator-(const Calibration& a)
{
    return Calibration(a.aveta(),
	    -a.calibparams()[0], -a.calibparams()[1],
	    a.calibparamcov()[0], a.calibparamcov()[1], a.calibparamcov()[2]);
}

/// C++ stream output
std::ostream& operator<<(std::ostream& os, const Calibration& c)
{ return c.print(os); }

TH1* getTemplate(const char* fname, const char* name)
{
    TFile f(fname, "READ");
    TH1* retVal = dynamic_cast<TH1*>(f.Get(name));
    assert(retVal);
    retVal->SetDirectory(0);
    // remove bins with content <= 0
    for (unsigned i = 0; i <= unsigned(retVal->GetNbinsX()) + 1; ++i) {
	const double c = retVal->GetBinContent(i);
	if (c < 0. || c != c || 0. == std::abs(1. / c)) {
	    retVal->SetBinContent(i, 0.);
	    retVal->SetBinError(i, 0.);
	}
    }
    return retVal;
}

DLLVector genUncorrTaggers(const DLLVector& tageffs,
	const TH1* mistagpdfs[N],
	const Calibration truecalib[N],
	const Calibration applycalib[N],
	TagTools::TagDec* trueDec = 0)
{
    assert(2 == N);
    // strategy:
    //
    // - we want this code to produce the same observables (tagging decisions
    //   and mistags) for the same random seed, independent of the true
    //   calibration of the taggers
    // - that means we have to throw the dice for the tagging decisions and the
    //   mistags first
    // - then, we generate the true flavour of the B in such a way that it's
    //   consistent with the observables (and the true calibration)
    //
    // that's the opposite of what you would normally do (decide the true B
    // flavour first, and then throw the dice to get tagging decisions for
    // given mistags). the reason to do it this way is purely that the
    // generated observables (mistags and tagging decisions) will only depend
    // on the seed for the generator (and the reference calibration), a
    // desirable thing when you have to compare results for different true
    // calibrations afterwards. still, the code respects all constraints
    // (tagging efficiencies, the events are tagged wrong in the right fraction
    // of cases...), so this is merely a trick to make the rest of the work
    // more convenient.
    using TagTools::evalCalibPoly;
    // we need a bunch of uniformly distributed random numbers
    double tmp[2 * N + 1];
    gRandom->RndmArray(2 * N + 1, tmp);
    double *tmp2 = &tmp[N], *tmp3 = &tmp[2 * N];
    // throw tagging decisions
    for (unsigned i = 0; i < N; ++i) tmp2[i] = (tmp2[i] > 0.5) ? 1.0 : -1.0;
    // mistags distributed according to their respective distributions
    double eta[N];
    for (unsigned i = 0; i < N; ++i) eta[i] = mistagpdfs[i]->GetRandom();
    // work out true etas (apply true calibration)
    double etatrue[N];
    for (unsigned i = 0; i < N; ++i) {
	if (tmp[i] > tageffs[i]) {
	    etatrue[i] = 0.5;
	} else {
	    etatrue[i] = evalCalibPoly(eta[i], truecalib[i].aveta(),
		    truecalib[i].calibparams());
	}
    }
    // ok, synthesize true flavour of the B
    TagTools::TagDec truth = TagTools::Untagged;
    if (tmp2[0] * tmp2[1] > 0.) {
	// taggers agree in their decision
	const double cc = (1. - etatrue[0]) * (1. - etatrue[1]);
	const double ii = etatrue[0] * etatrue[1];
	if (*tmp3 > ii / (cc + ii)) {
	    // both taggers got it right
	    truth = static_cast<TagTools::TagDec>(+int(tmp2[0]));
	} else {
	    // both taggers got it wrong
	    truth = static_cast<TagTools::TagDec>(-int(tmp2[0]));
	}
    } else {
	// taggers disagree in their decision
	const double ci = (1. - etatrue[0]) * etatrue[1];
	const double ic = etatrue[0] * (1. - etatrue[1]);
	if (*tmp3 > ic / (ic + ci)) {
	    // first tagger got it right, second one wrong
	    truth = static_cast<TagTools::TagDec>(+int(tmp2[0]));
	} else {
	    // first tagger got it wrong, second one right
	    truth = static_cast<TagTools::TagDec>(-int(tmp2[0]));
	}
    }
    assert(TagTools::Untagged != truth);
    // save true B flavour (if so desired)
    if (trueDec) *trueDec = truth;
    // ok, write output (apply reference calibration in applycalib on the
    // way...)
    DLLVector retVal;
    for (unsigned i = 0; i < N; ++i) {
	if (tmp[i] > tageffs[i]) {
	    // untagged event - easy
	    retVal[i] = TagTools::tagDLL(TagTools::Untagged, 0.5);
	} else {
	    // tagged event - use tagging decision, and apply the reference
	    // calibration in applycalib
	    retVal[i] = TagTools::tagDLL(
		    static_cast<TagTools::TagDec>(int(tmp2[i])),
		    evalCalibPoly(eta[i], applycalib[i].aveta(),
			applycalib[i].calibparams()));
	}
    }
    return retVal;
}

/// hold the final calibration with all its uncertainties
class OutCalibration
{
    public:
	/// encode what is being updated
	typedef enum { B = 0, Bbar = 6 } InitialFlavour;
	/// encode what is being updated
	typedef enum { OSOnly = 0, SSKOnly = 2, OSSSK = 4 } TagCategory;
	/// encode what is being updated
	typedef enum { P0 = 0, P1 = 1 } CalibCoeff;

    public:
	OutCalibration()
	{
	    std::fill(m_aveta, m_aveta + 3,
		    std::numeric_limits<double>::quiet_NaN());
	    std::fill(m_calib, m_calib + 12,
		    std::numeric_limits<double>::quiet_NaN());
	    std::fill(m_cov, m_cov + (12 * 13 / 2),
		    std::numeric_limits<double>::quiet_NaN());
	}

	/// constructor
	OutCalibration(
		const std::vector<Calibration>& calib)
	{
	    assert(6 == calib.size());
	    assert(calib[0].aveta() == calib[3].aveta());
	    assert(calib[1].aveta() == calib[4].aveta());
	    assert(calib[2].aveta() == calib[5].aveta());

	    m_aveta[0] = calib[0].aveta();
	    m_aveta[1] = calib[1].aveta();
	    m_aveta[2] = calib[2].aveta();

	    m_calib[B+OSOnly +P0] = calib[0].calibparams()[0];
	    m_calib[B+OSOnly +P1] = calib[0].calibparams()[1];
	    m_calib[B+SSKOnly+P0] = calib[1].calibparams()[0];
	    m_calib[B+SSKOnly+P1] = calib[1].calibparams()[1];
	    m_calib[B+OSSSK  +P0] = calib[2].calibparams()[0];
	    m_calib[B+OSSSK  +P1] = calib[2].calibparams()[1];
	    m_calib[Bbar+OSOnly +P0] = calib[3].calibparams()[0];
	    m_calib[Bbar+OSOnly +P1] = calib[3].calibparams()[1];
	    m_calib[Bbar+SSKOnly+P0] = calib[4].calibparams()[0];
	    m_calib[Bbar+SSKOnly+P1] = calib[4].calibparams()[1];
	    m_calib[Bbar+OSSSK  +P0] = calib[5].calibparams()[0];
	    m_calib[Bbar+OSSSK  +P1] = calib[5].calibparams()[1];

	    // fill covariance matrix
	    std::fill(m_cov, m_cov + 12 * 13 / 2, 0.);
	    // copy over stat. part of cov matrix
	    for (unsigned i = 0; i < 6; ++i) {
		for (unsigned j = 0; j < 2; ++j) {
		    const unsigned jj = 2 * i + j;
		    for (unsigned k = 0; k <= j; ++k) {
			const unsigned kk = 2 * i + k;
			m_cov[(jj * (jj + 1)) / 2 + kk] =
			    calib[i].calibparamcov()[(j * (j + 1)) / 2 + k];
		    }
		}
	    }
	}

	/// retrieve average eta
	double getAvEta(TagCategory cat) const
	{ return m_aveta[int(cat) / 2]; }

	/// update covariance matrix with scale^2 other * other^T (i.e. other = (scale d\vec{outcal}/ddeltaincal) * deltaincal)
	void updateCov(const OutCalibration& other, const double scale = 1.0)
	{
	    // check that we're based on same averages
	    assert(other.m_aveta[0] == m_aveta[0]);
	    assert(other.m_aveta[1] == m_aveta[1]);
	    assert(other.m_aveta[2] == m_aveta[2]);

	    // form difference to nominal calibration
	    double d[12];
	    for (unsigned i = 0; i < 12; ++i) d[i] = scale * other.m_calib[i];
	    // update covariance matrix
	    for (unsigned i = 0; i < 12; ++i)
		for (unsigned j = 0; j <= i; ++j)
		    m_cov[(i * (i + 1) / 2) + j] += d[i] * d[j];
	}

	Calibration getOutCalib(InitialFlavour iflav, TagCategory cat) const
	{
	    const int ip0 = iflav + cat + P0, ip1 = iflav + cat + P1;
	    return Calibration(
		    m_aveta[cat / SSKOnly], m_calib[ip0], m_calib[ip1],
		    m_cov[(ip0 * (ip0 + 1)) / 2 + ip0],
		    m_cov[(ip1 * (ip1 + 1)) / 2 + ip1 - 1],
		    m_cov[(ip1 * (ip1 + 1)) / 2 + ip1]);
	}

	std::ostream& print(std::ostream& os) const
	{
	    static const char *flav[2] = { "B   ", "Bbar" };
	    static const char *cat[3] = { "OS only ", "SSK only", "OS + SSK" };

	    std::ios::fmtflags oflags = os.flags();
	    os.setf(std::ios::fixed, std::ios::floatfield);
	    std::streamsize ow = os.width(), op = os.precision();

	    for (unsigned ifl = 0; ifl < 2; ++ifl) {
		for (unsigned icat = 0; icat < 3; ++icat) {
		    os << flav[ifl] << " " << cat[icat] << ": " <<
			getOutCalib(static_cast<InitialFlavour>(ifl * Bbar),
				static_cast<TagCategory>(icat * SSKOnly)) <<
			std::endl;
		}
	    }

	    os << std::endl << "Correlations:" << std::endl;
	    os << "  ";
	    for (unsigned i = 0; i < 12; ++i)
		os << " " << std::setw(12) << i;
	    os << std::endl;
	    for (unsigned i = 0; i < 12; ++i) {
		os << std::setw(2) << i;
		const unsigned iidx = ((i * (i + 1)) / 2 + i);
		for (unsigned j = 0; j < 12; ++j) {
		    const unsigned idx = (i >= j) ?
			((i * (i + 1)) / 2 + j) :
			((j * (j + 1)) / 2 + i);
		    const unsigned jidx = ((j * (j + 1)) / 2 + j);
		    const double correl = m_cov[idx] /
			std::sqrt(m_cov[iidx] * m_cov[jidx]);
		    os << " " << std::setw(12) <<
			std::setprecision(9) << correl;
		}
		os << std::endl;
	    }

	    os.flags(oflags);
	    os.width(ow);
	    os.precision(op);

	    return os;
	}

	OutCalibration& operator+=(const OutCalibration& other)
	{
	    assert(m_aveta[0] == other.m_aveta[0]);
	    assert(m_aveta[1] == other.m_aveta[1]);
	    assert(m_aveta[2] == other.m_aveta[2]);
	    for (unsigned i = 0; i < 12; ++i) m_calib[i] += other.m_calib[i];
	    for (unsigned i = 0; i < 12 * 13 / 2; ++i) m_cov[i] += other.m_cov[i];
	    return *this;
	}

	OutCalibration& operator-=(const OutCalibration& other)
	{
	    assert(m_aveta[0] == other.m_aveta[0]);
	    assert(m_aveta[1] == other.m_aveta[1]);
	    assert(m_aveta[2] == other.m_aveta[2]);
	    for (unsigned i = 0; i < 12; ++i) m_calib[i] -= other.m_calib[i];
	    for (unsigned i = 0; i < 12 * 13 / 2; ++i) m_cov[i] += other.m_cov[i];
	    return *this;
	}

    private:
	double m_aveta[3];
	double m_calib[12];
	double m_cov[12 * 13 / 2];
};

std::ostream& operator<<(std::ostream& os, const OutCalibration& c)
{ return c.print(os); }

OutCalibration operator+(const OutCalibration& a, const OutCalibration& b)
{ return OutCalibration(a) += b; }

OutCalibration operator-(const OutCalibration& a, const OutCalibration& b)
{ return OutCalibration(a) -= b; }

/// get approximate subtraction to cancel correlations based on mistag distribution
double getEVal(const TH1& h)
{
    double sumw2 = 0., sumetaw2 = 0.;
    for (unsigned i = 1; i <= unsigned(h.GetNbinsX()); ++i) {
	const double e = h.GetBinContent(i);
	// skip empty/invalid bins
	if (e != e || e <= 0.) continue;
	const double eta = h.GetBinCenter(i);
	const double w = e / (eta * (1. - eta));
	sumw2 += w;
	sumetaw2 += w * eta;
    }
    std::cout << "DEBUG: mean " << h.GetMean() << " eVal " << (sumetaw2 / sumw2) << std::endl;

    return sumetaw2 / sumw2;
}

class CombinerSimulation
{
    private:
	Calibration m_incalibnominal[2];	///< nominal calibration
	Calibration m_incalibstaterr[2];	///< statistical error on calib.
	Calibration m_incalibsysterr[2];	///< systematic error on calib.
	Calibration m_incalibdeltaphalf[2];	///< 0.5 * delta p0/p1 (B/Bbar)
	Calibration m_incalibdeltaphalferr[2];	///< error on m_calibdeltaphalf


	OutCalibration m_outnominal;
	OutCalibration m_outstat;
	OutCalibration m_outstatdeltaphalf;
	OutCalibration m_outsyst;
	OutCalibration m_outtotal;

	template <class T> class ObjSwapper {
	    private:
		T* m_old;
		T*& m_dstobj;
		ObjSwapper(const ObjSwapper<T>&);
		ObjSwapper<T>& operator=(const ObjSwapper<T>&);
	    public:
		ObjSwapper(T*& dstobj, T* newobj) : m_old(newobj), m_dstobj(dstobj)
	        { std::swap(m_dstobj, m_old); }
		~ObjSwapper()
	        { std::swap(m_dstobj, m_old); delete m_old; }
	};

	/// run a toy for a single set of calibrations
	std::vector<Calibration> runToy(
		const Calibration nominalcalib[2],
		const Calibration truecalib[2]) const
	{
	    std::vector<Calibration> outcalib;
	    outcalib.reserve(3);

	    const TH1* templates[2] = { 
		getTemplate("templates.root", "etaOS"),
		getTemplate("templates.root", "etaSSK")
	    };

	    // 2^26 events in toy (so fits are nice and stable)
	    const unsigned long nevts = 1 << 26;
	    std::cout << "Using " << nevts << " events per sample" << std::endl;

	    // print inputs
	    const std::string inlabels[2] = { " OS", "SSK" };
	    for (unsigned i = 0; i < 2; ++i) {
		std::cout << "True calibration for " << inlabels[i] << " events: " <<
		    truecalib[i] << std::endl;
		std::cout << "Apply calibration to " << inlabels[i] << " events: " <<
		    nominalcalib[i] << std::endl;
	    }

	    const std::string labels[3] = { " OS only", "SSK only", "  OS+SSK" };
	    // run for OS only, SSK only, both OS and SSK
	    for (unsigned irun = 1; irun < 4; ++irun) {
		TH1D h_eta("eta", "eta;eta;#", 100, 0., 0.5);
		TH1D h_omega("omega", "omega;eta;omega", 100, 0., 0.5);
		h_eta.Sumw2();
		h_omega.Sumw2();

		const DLLVector tageffs(1.0 * bool(irun & 1), 1.0 * bool(irun & 2));
		std::cout << "Simulating " << labels[irun - 1] << " events" << std::endl;

		ObjSwapper<TRandom> gRandomSwapper(gRandom, new TRandom3(42));
		// use our own PRNG
		TagTools::TagCombiner<N> combiner;
		for (unsigned long iev = 0; iev < nevts; ++iev) {
		    TagTools::TagDec truth;
		    DLLVector taggers(genUncorrTaggers(
				tageffs, templates, truecalib, nominalcalib, &truth));
		    const double dll = combiner.combine(taggers);
		    TagTools::TagDec dec = TagTools::tagDec(dll);
		    if (TagTools::Untagged != dec) {
			double eta = TagTools::tagEta(dll);
			h_eta.Fill(eta);
			if (dec != truth) h_omega.Fill(eta);
		    }
		}

		h_omega.Divide(&h_omega, &h_eta, 1., 1., "B");
		// select fitter
#if 0
		// straight line fit using Minuit (overkill, except if you want plots)
		TF1 calib("calib", Form("[0] + [1]*(x - %g)", h_eta.GetMean()), 0., 0.5);
		calib.SetParameters(h_eta.GetMean(), 1.0);
		h_omega.Fit(&calib, "NQ");
		// save calibration we obtained
		TVirtualFitter *fitter = TVirtualFitter::GetFitter();
		outcalib.push_back(Calibration(
			    h_eta.GetMean(),
			    calib.GetParameter(0),
			    calib.GetParameter(1),
			    fitter->GetCovarianceMatrixElement(0, 0),
			    fitter->GetCovarianceMatrixElement(1, 0),
			    fitter->GetCovarianceMatrixElement(1, 1)));
#else	    
		// fast and accurate analytical chi^2 fit
		outcalib.push_back(Calibration(
			    //h_eta.GetMean(), --- don't use this!
			    getEVal(h_eta),
			    &h_omega));
#endif
	    }

	    delete templates[0]; delete templates[1];

	    std::cout << std::endl;
	    for (unsigned i = 1; i < 4; ++i) {
		std::cout << "Calibration for " << labels[i - 1] << ": " <<
		    outcalib[i - 1] << std::endl;
	    }
	    std::cout << std::endl;

	    return outcalib;
	}

	/// run toys for B/Bbar for a single set of calibrations
	OutCalibration runToys(
		const Calibration nominalcalib[2][2],
		const Calibration truecalib[2][2]) const
	{
	    // first B
	    std::vector<Calibration> calib =
		runToy(nominalcalib[0], truecalib[0]);
	    // then Bbar
	    std::vector<Calibration> tmpcalib =
		runToy(nominalcalib[1], truecalib[1]);
	    // merge
	    calib.insert(calib.end(), tmpcalib.begin(), tmpcalib.end());
	    tmpcalib.clear();
	    // construct output
	    return OutCalibration(calib);
	}

	/// run OS p0/p1 and SSK p0/p1 variations for B/Bbar
	std::vector<OutCalibration> runToysVariationOneAtATime(
		const Calibration nominalcalib[2][2],
		const Calibration truecalib[2][2],
		const Calibration deltacalib[2][2]) const
	{
	    std::vector<OutCalibration> retVal, tmp;
	    retVal.reserve(4); tmp.reserve(8);
	    // up/downward variation of the four parameters
	    for (unsigned i = 0; i < 8; ++i) {
		const double sign = (i & 1) ? -1.0 : 1.0;
		const Calibration tmpcal[2][2] = {
		    {
			Calibration(truecalib[0][0].aveta(), // OS (B)
				truecalib[0][0].calibparams()[0] + sign *
				((0 == (i / 2)) ? deltacalib[0][0].calibparams()[0] : 0.),
				truecalib[0][0].calibparams()[1] + sign *
				((1 == (i / 2)) ? deltacalib[0][0].calibparams()[1] : 0.)),
			Calibration(truecalib[0][1].aveta(), // OS (B)
				truecalib[0][1].calibparams()[0] + sign *
				((2 == (i / 2)) ? deltacalib[0][1].calibparams()[0] : 0.),
				truecalib[0][1].calibparams()[1] + sign *
				((3 == (i / 2)) ? deltacalib[0][1].calibparams()[1] : 0.))
		    }, {
			Calibration(truecalib[1][0].aveta(), // OS (Bbar)
				truecalib[1][0].calibparams()[0] + sign *
				((0 == (i / 2)) ? deltacalib[1][0].calibparams()[0] : 0.),
				truecalib[1][0].calibparams()[1] + sign *
				((1 == (i / 2)) ? deltacalib[1][0].calibparams()[1] : 0.)),
			Calibration(truecalib[1][1].aveta(), // OS (Bbar)
				truecalib[1][1].calibparams()[0] + sign *
				((2 == (i / 2)) ? deltacalib[1][1].calibparams()[0] : 0.),
				truecalib[1][1].calibparams()[1] + sign *
				((3 == (i / 2)) ? deltacalib[1][1].calibparams()[1] : 0.))
		    }
		};
		tmp.push_back(runToys(nominalcalib, tmpcal));
	    }
	    // form "average", or really (as required by error propagation)
	    // 2 * (d\vec{f}/dp_i) sigma_p_i
	    for (unsigned i = 0; i < 4; ++i) {
		retVal.push_back(tmp[2 * i] - tmp[2 * i + 1]);
	    }
	    return retVal;
	}

    public:
	CombinerSimulation(
		const Calibration& incalibOS,
		const Calibration& incalibOSerrstat,
		const Calibration& incalibOSerrsyst,
		const Calibration& incalibOSdeltaPhalf,
		const Calibration& incalibOSdeltaPhalferr,
		const Calibration& incalibSSK,
		const Calibration& incalibSSKerrstat,
		const Calibration& incalibSSKerrsyst,
		const Calibration& incalibSSKdeltaPhalf,
		const Calibration& incalibSSKdeltaPhalferr)
	{
	    m_incalibnominal[0] = incalibOS;
	    m_incalibstaterr[0] = incalibOSerrstat;
	    m_incalibsysterr[0] = incalibOSerrsyst;
	    m_incalibdeltaphalf[0] = incalibOSdeltaPhalf;
	    m_incalibdeltaphalferr[0] = incalibOSdeltaPhalferr;
	    m_incalibnominal[1] = incalibSSK;
	    m_incalibstaterr[1] = incalibSSKerrstat;
	    m_incalibsysterr[1] = incalibSSKerrsyst;
	    m_incalibdeltaphalf[1] = incalibSSKdeltaPhalf;
	    m_incalibdeltaphalferr[1] = incalibSSKdeltaPhalferr;

	    const Calibration nominal[2][2] = {
		{ m_incalibnominal[0], m_incalibnominal[1] },
		{ m_incalibnominal[0], m_incalibnominal[1] }
	    };
	    // B/Bbar is nominal +/- (delta p_0/2, delta p_1/2)
	    const Calibration truecal[2][2] = {
		{ m_incalibnominal[0] + m_incalibdeltaphalf[0],
		    m_incalibnominal[1] + m_incalibdeltaphalf[1] },
		{ m_incalibnominal[0] - m_incalibdeltaphalf[0],
		    m_incalibnominal[1] - m_incalibdeltaphalf[1] }
	    };

	    m_outnominal = runToys(nominal, truecal);

	    m_outstat = m_outstatdeltaphalf = m_outsyst = m_outtotal = m_outnominal;

	    // ok, get the stat error influence
	    const Calibration deltastat[2][2] = {
		{ m_incalibstaterr[0], m_incalibstaterr[1] },
		{ m_incalibstaterr[0], m_incalibstaterr[1] }
	    };

	    std::vector<OutCalibration> tmp = runToysVariationOneAtATime(nominal, truecal, deltastat);
	    for (std::vector<OutCalibration>::const_iterator it = tmp.begin();
		    tmp.end() != it; ++it) {
		m_outstat.updateCov(*it, 0.5);
		m_outtotal.updateCov(*it, 0.5);
	    }

	    // ok, get the stat error influence (deltaPHalf)
	    const Calibration deltadeltaphalfstat[2][2] = {
		{ m_incalibdeltaphalferr[0], m_incalibdeltaphalferr[1] },
		{ - m_incalibdeltaphalferr[0], - m_incalibdeltaphalferr[1] }
	    };

	    tmp = runToysVariationOneAtATime(nominal, truecal, deltadeltaphalfstat);
	    for (std::vector<OutCalibration>::const_iterator it = tmp.begin();
		    tmp.end() != it; ++it) {
		m_outstatdeltaphalf.updateCov(*it, 0.5);
		m_outtotal.updateCov(*it, 0.5);
	    }

	    // ok, get the syst error influence
	    const Calibration deltasyst[2][2] = {
		{ m_incalibsysterr[0], m_incalibsysterr[1] },
		{ m_incalibsysterr[0], m_incalibsysterr[1] }
	    };

	    tmp = runToysVariationOneAtATime(nominal, truecal, deltasyst);
	    for (std::vector<OutCalibration>::const_iterator it = tmp.begin();
		    tmp.end() != it; ++it) {
		m_outsyst.updateCov(*it, 0.5);
		m_outtotal.updateCov(*it, 0.5);
	    }
	}

	std::ostream& print(std::ostream& os) const
	{
	    os << "Nominal calibration:" << std::endl <<
		m_outnominal << std::endl << std::endl;
	    os << "Stat. error calibration:" << std::endl <<
		m_outstat << std::endl << std::endl;
	    os << "Stat. error (Delta P / 2) calibration:" << std::endl <<
		m_outstatdeltaphalf << std::endl << std::endl;
	    os << "Syst. error calibration:" << std::endl <<
		m_outsyst << std::endl << std::endl;
	    os << "Total calibration:" << std::endl <<
		m_outtotal << std::endl << std::endl;
	    return os;
	}

    private:
};

int main(int /*argc*/, char* /*argv*/[])
{

    const Calibration nominal[2] = {
	Calibration(0.3813, 0.3834, 0.972), // OS:  aveta, p0, p1
	Calibration(0.4097, 0.4244, 1.218), // SSK: aveta, p0, p1
    };
    const Calibration staterr[2] = {
	Calibration(0.3813, 0.0014, 0.012), // OS
	Calibration(0.4097, 0.0086, 0.150)  // SSK
    };
    const Calibration systerr[2] = {
	Calibration(0.3813, 0.0040, 0.035), // OS
	Calibration(0.4097, 0.0071, 0.104)  // SSK
    };
    const Calibration deltaPHalf[2] = {
	Calibration(0.3813, 0.5 * 0.0124, 0.5 * 0.095), // OS
	Calibration(0.4097, 0.5 * -0.020, 0.5 * -0.01)  // SSK
    };
    const Calibration deltaPHalfErr[2] = {
	Calibration(0.3813, 0.5 * 0.0021, 0.5 * 0.024), // OS
	Calibration(0.4097, 0.5 *  0.004, 0.5 *  0.03)  // SSK
    };

    CombinerSimulation up(
	    nominal[0], staterr[0], systerr[0], deltaPHalf[0], deltaPHalfErr[0],
	    nominal[1], staterr[1], systerr[1], deltaPHalf[1], deltaPHalfErr[1]);
    up.print(std::cout);

    return 0;
}
