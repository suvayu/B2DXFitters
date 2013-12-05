#include <cmath>
#include <cassert>
#include <iostream>
#include <algorithm>

#include "TRandom.h"
#include "TRandom3.h"
#include "TFile.h"
#include "Math/SVector.h"

#include "TH1D.h"
#include "TF1.h"
#include "TPad.h"
#include "TStyle.h"

#include "../B2DXFitters/TagCombiner.h"

enum { N = 2 };

typedef ROOT::Math::SVector<double, N> DLLVector;

struct Calibration {
    double aveta;
    double calibparams[2]; // p0, p1
    double calibparamerrs[2];
};

std::ostream& operator<<(std::ostream& os, const Calibration& c)
{
    os << "eta_c = " << c.calibparams[0];
    if (c.calibparamerrs[0] > 0.)
	os << "+/-" << c.calibparamerrs[0];
    os << " + (" << c.calibparams[1];
    if (c.calibparamerrs[1] > 0.)
	os << "+/-" << c.calibparamerrs[1];
    os << ") * (eta - " << c.aveta << ")";
    return os;
}

TRandom* gen = 0;
TRandom* oldgen = 0;

TH1* getTemplate(const char* fname, const char* name)
{
    TFile f(fname, "READ");
    TH1* retVal = dynamic_cast<TH1*>(f.Get(name));
    assert(retVal);
    retVal->SetDirectory(0);
    // remove bins with content <= 0
    for (unsigned i = 0; i <= unsigned(retVal->GetNbinsX()) + 1; ++ i) {
	const double c = retVal->GetBinContent(i);
	if (c < 0. || c != c || 0. == std::abs(1. / c )) {
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
    gen->RndmArray(2 * N + 1, tmp);
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
	    etatrue[i] = evalCalibPoly<2>(eta[i], truecalib[i].aveta,
		    truecalib[i].calibparams);
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
		    evalCalibPoly<2>(eta[i], applycalib[i].aveta,
			applycalib[i].calibparams));
	}
    }
    return retVal;
}

int main(int argc, char* argv[])
{
    if (5 != argc) {
	std::cout << "usage: " << argv[0] <<
	    " dp0_OS dp1_OS dp0_SSK dp1_SSK" << std::endl <<
	    "\tdp0_OS\tamount by which to shift p0 of OS calibration" <<
	    std::endl <<
	    "\tdp1_OS\tamount by which to shift p1 of OS calibration" <<
	    std::endl <<
	    "\tdp0_SSK\tamount by which to shift p0 of SSK calibration" <<
	    std::endl <<
	    "\tdp1_SSK\tamount by which to shift p1 of SSK calibration" <<
	    std::endl;
	return -1;
    }
    oldgen = gen = new TRandom3(42);
    std::swap(gRandom, oldgen);
    gStyle->SetOptStat(0);

    const TH1* templates[2] = {
	getTemplate("templates.root", "etaOS"),
	getTemplate("templates.root", "etaSSK")
    };
    // we modify the true calibration (it governs what the true mistag is)
    Calibration truecalib[2] = {
	{ 0.3919, { 0.3927 + std::atof(argv[1]), 0.9818 + std::atof(argv[2]) },
	    { 0., 0. } },
	{ 0.4097, { 0.4244 + std::atof(argv[3]), 1.255 + std::atof(argv[4]) },
	    { 0., 0. } }
    };
    // but always apply the same nominal calibration before combining
    Calibration applycalib[2] = {
	{ 0.3919, { 0.3927,  0.9818 }, { 0., 0. } },
	{ 0.4097, { 0.4244, 1.255 }, { 0., 0. } }
    };
    // by how much to calibrate after the combination to undo the fact that
    // applycalib is off wrt. truecalib
    Calibration postcalib[3];

    // 2^26 events in toy (so fits are nice and stable)
    const unsigned long nevts = 1 << 26;

    TH1D h_eta("eta", "eta;eta;#", 100, 0., 0.5);
    TH1D h_omega("omega", "omega;eta;omega", 100, 0., 0.5);
    h_eta.Sumw2();
    h_omega.Sumw2();

    // print inputs
    const std::string inlabels[2] = { " OS", "SSK" };
    for (unsigned i = 0; i < 2; ++i) {
	std::cout << "True calibration for " << inlabels[i] << " events: " <<
	    truecalib[i] << std::endl;
	std::cout << "Apply calibration to " << inlabels[i] << " events: " <<
	    applycalib[i] << std::endl;
    }
    std::cout << "Using " << nevts << " events per sample" << std::endl;

    const std::string labels[3] = { " OS only", "SSK only", "  OS+SSK" };
    // run for OS only, SSK only, both OS and SSK
    for (unsigned irun = 1; irun < 4; ++irun) {
	gen->SetSeed(42);
	const DLLVector tageffs(1.0 * bool(irun & 1), 1.0 * bool(irun & 2));
	std::cout << "Simulating " << labels[irun - 1] << " events" << std::endl;

	h_eta.Reset();
	h_omega.Reset();

	TagTools::TagCombiner<N> combiner;
	for (unsigned long iev = 0; iev < nevts; ++iev) {
	    TagTools::TagDec truth;
	    DLLVector taggers(genUncorrTaggers(
			tageffs, templates, truecalib, applycalib, &truth));
	    const double dll = combiner.combine(taggers);
	    TagTools::TagDec dec = TagTools::tagDec(dll);
	    if (TagTools::Untagged != dec) {
		double eta = TagTools::tagEta(dll);
		h_eta.Fill(eta);
		if (dec != truth) h_omega.Fill(eta);
	    }
	}

	h_eta.Draw();
	gPad->Print(Form("eta%u.eps", irun));
	h_omega.Divide(&h_omega, &h_eta, 1., 1.);
	TF1 calib("calib", Form("[0] + [1]*(x - %g)", h_eta.GetMean()), 0., 0.5);
	calib.SetParameters(h_eta.GetMean(), 1.0);
	TF1 idcalib(calib);
	calib.SetLineColor(kBlue);
	h_omega.Fit(&calib, "QI");
	// save calibration we obtained
	postcalib[irun - 1].aveta = h_eta.GetMean();
	postcalib[irun - 1].calibparams[0] = calib.GetParameter(0);
	postcalib[irun - 1].calibparams[1] = calib.GetParameter(1);
	postcalib[irun - 1].calibparamerrs[0] = calib.GetParError(0);
	postcalib[irun - 1].calibparamerrs[1] = calib.GetParError(1);
	h_omega.Draw();
	idcalib.Draw("SAME");
	gPad->Print(Form("omega%u.eps", irun));
    }
    std::swap(gRandom, oldgen);
    delete gen;

    // all done, print report
    std::cout << std::endl;
    for (unsigned i = 1; i < 4; ++i) {
	std::cout << "Post-calibration for " << labels[i - 1] << ": " <<
	    postcalib[i - 1] << std::endl;
    }
    std::cout << std::endl;
    return 0;
}
