#include <cmath>
#include <cassert>
#include <iostream>
#include <algorithm>

#include "TRandom.h"
#include "TRandom3.h"
#include "TFile.h"
#include "Math/SVector.h"
#include "Math/SMatrix.h"

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
    using TagTools::evalCalibPoly;
    DLLVector tmp, tmp2, eta;
    // we need a bunch of uniformly distributed random numbers
    gen->RndmArray(N, tmp.Array());
    gen->RndmArray(N, tmp2.Array());
    // mistags distributed according to their respective distributions
    for (unsigned i = 0; i < N; ++i) eta[i] = mistagpdfs[i]->GetRandom();
    // true B flavour
    TagTools::TagDec truth = (gen->Rndm() > 0.5) ? TagTools::B : TagTools::Bbar;
    if (trueDec) *trueDec = truth;
    DLLVector retVal;
    for (unsigned i = 0; i < N; ++i) {
	if (tmp[i] > tageffs[i]) {
	    // untagged event - easy
	    retVal[i] = TagTools::tagDLL(TagTools::Untagged, 0.5);
	} else {
	    // tagged event - did we mistag?
	    // (apply the true calibration here to decide if we tagged
	    // correctly or not)
	    if (tmp2[i] <= evalCalibPoly<2>(eta[i], truecalib[i].aveta,
			truecalib[i].calibparams)) {
		// incorrect tag
		// (apply calibration - this is not the true calibration,
		// because we have to allow for the fact that the true
		// calibration is not precisely known)
		retVal[i] = TagTools::tagDLL(
			static_cast<TagTools::TagDec>(int(-truth)),
			evalCalibPoly<2>(eta[i], applycalib[i].aveta,
			    applycalib[i].calibparams));
	    } else {
		// correct tag
		// (apply calibration - this is not the true calibration,
		// because we have to allow for the fact that the true
		// calibration is not precisely known)
		retVal[i] = TagTools::tagDLL(
			static_cast<TagTools::TagDec>(int(+truth)),
			evalCalibPoly<2>(eta[i], applycalib[i].aveta,
			    applycalib[i].calibparams));
	    }
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
    return 0;
}
