/**
 * @file   RooSimultaneousResModel.cxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Fri Aug 30 15:19:15 2013
 *
 * @brief  Implementation file for RooSimultaneousResModel.
 *
 */

//////////////////////////////////////////////////////////////////////////////
//
// BEGIN_HTML
// Class RooSimultaneousResModel implements a RooResolutionModel that models an
// internal k-factor correction for other resolution models.  Object
// of class RooSimultaneousResModel can be used for analytical convolutions with
// classes inheriting from RooAbsAnaConvPdf
// END_HTML
//

#include <cstring>
#include <cmath>
#include <string>
#include <memory>
#include <limits>
#include <cassert>

#include "RooProduct.h"
#include "RooCustomizer.h"
#include "RooFormulaVar.h"
#include "RooNameSet.h"
#include "B2DXFitters/RooSimultaneousResModel.h"
#include "RooHistPdf.h"
#include "RooRealVar.h"
#include "RooCachedReal.h"

#include "TPad.h"
#include "RooPlot.h"

RooArgSet RooSimultaneousResModel::s_emptyset;

///////////////////////////////////
// DeceptiveCache implementation //
///////////////////////////////////

RooSimultaneousResModel::DeceptiveCache::DeceptiveCache(const RooSimultaneousResModel& parent,
	const RooArgSet& iset,
	const char* rangeName) :
    _cval(std::numeric_limits<double>::quiet_NaN()),
    _kvar(0), _kpdf(0), _val(0), _parent(parent)
{
    // build a (hopefully unique) suffix for objects we have to clone/modify
    std::string sfx = "_DeceptiveCache_";
    sfx += RooNameSet(iset).content();
    if (rangeName && std::strlen(rangeName)) {
	    sfx += "_";
	    sfx += rangeName;
    }

    const RooAbsRealLValue& kvar = parent.kvar();
    const RooHistPdf& kpdf = parent.kpdf();
    // get k-bin boundaries
    {
	const double kmin = kvar.getMin();
	const double kmax = kvar.getMax();
	std::auto_ptr<std::list<Double_t> > kbins(kpdf.binBoundaries(
		    const_cast<RooAbsRealLValue&>(kvar), kmin, kmax));
	assert(kbins.get());
	assert(kbins->size() > 1);	// at least 2 bins
	for (std::list<Double_t>::const_iterator lo = kbins->begin(),
		hi = ++(kbins->begin()); hi != kbins->end(); ++lo, ++hi) {
	    // check interval
	    if (*lo > kmax) break;    // past interval
	    if (*hi < kmin) continue; // before interval
	    if (_kbins.empty()) _kbins.push_back(std::max(*lo, kmin));
	    _kbins.push_back(std::min(*hi, kmax));
	}
    }

    _kvar = dynamic_cast<RooRealVar*>(kvar.clone((std::string(kvar.GetName()) + sfx).c_str()));
    assert(_kvar);
    _knset.add(*_kvar);
    {
	RooCustomizer c(kpdf, sfx.c_str());
	c.replaceArg(kvar, *_kvar);
	_kpdf = dynamic_cast<RooHistPdf*>(c.build());
    }

    const RooResolutionModel& resmodel = parent.resmodel();
    // check if we need to integrate the resmodel
    const RooAbsReal* cache = &resmodel;
    if (iset.getSize()) {
	cache = resmodel.createIntegral(iset, rangeName);
    }
    assert(cache);

    // customise resolution model
    {
	RooCustomizer c(*cache, sfx.c_str());
	// get list of terms t in resmodel that may need replacement t -> k * t
	RooArgSet params;
	resmodel.treeNodeServerList(&params);

	RooArgSet new_paramset;
	RooFIter it = params.fwdIterator();
	for (RooAbsReal* param = dynamic_cast<RooAbsReal*>(it.next()); param;
		param = dynamic_cast<RooAbsReal*>(it.next())) {
	    if (!parent._substTargets.find(*param)) continue;
	    std::string parname(param->GetName());
	    parname += "_x_"; parname += _kvar->GetName();
	    RooProduct *new_param = new RooProduct(parname.c_str(), parname.c_str(),
		    RooArgList(*param, *_kvar));
	    assert(new_param);
	    c.replaceArg(*param, *new_param);
	    new_paramset.add(*new_param);
	}
	// build copy of resolution model with substitutions applied
	_val = dynamic_cast<RooAbsReal*>(c.build());
	assert(_val);
	_val->addOwnedComponents(new_paramset); // new resmodel owns params (k*old)
    }
    _val->setValueDirty();
    _val->setShapeDirty();

    if (cache != &resmodel) delete cache;	  // clean-up when integral
}

RooSimultaneousResModel::DeceptiveCache::~DeceptiveCache()
{
    delete _val;
    delete _kpdf;
    _knset.removeAll();
    delete _kvar;
}

RooArgList RooSimultaneousResModel::DeceptiveCache::containedArgs(RooAbsCacheElement::Action)
{
    // Return list of all RooAbsArgs in cache element
    return RooArgList(*_val, *_kpdf, *_kvar);
}

double RooSimultaneousResModel::DeceptiveCache::getVal(const RooArgSet* nset) const
{
    // see if our cached value needs recalculating
    if (_cval != _cval || _val->isValueOrShapeDirtyAndClear()) {
	// evaluate: calculate _val
	const unsigned nbins = _kbins.size() - 1;
	_cval = 0.;
	for (unsigned bin = 0; bin < nbins; ++bin) {
	    const Double_t bincentre = 0.5 * (_kbins[bin] + _kbins[bin + 1]);
	    const Double_t binwidth = _kbins[bin + 1] - _kbins[bin];
	    _kvar->setVal(bincentre);
	    // ok, get value of kpdf (times bin width)
	    const Double_t tmp1 = _kpdf->getVal(_knset) * binwidth;
	    if (std::isnan(tmp1) || std::isinf(tmp1)) {
		// NaN or Inf - should never happen
		oocoutE(&_parent, Eval) << "In " << __func__ << "(" << __FILE__ <<
		    ", line " << __LINE__ << "), object " << this << " (_kpdf = " <<
		    _kpdf << " _val = " << _val << "): got " << tmp1 << " for "
		    "_kpdf * binwidth!" << std::endl;
		// break return value deliberately
		return (_cval = std::numeric_limits<Double_t>::quiet_NaN());
	    } else if (0. == tmp1) {
		// bin cannot contribute, so that's fine...
		continue;
	    }
	    // get value of _val for this k
	    const Double_t tmp2 = _val->getVal(nset);
	    if (std::isnan(tmp2) || std::isinf(tmp2)) {
		// NaN or Inf - should never happen
		oocoutE(&_parent, Eval) << "In " << __func__ << "(" << __FILE__ <<
		    ", line " << __LINE__ << "), object " << this << " (_kpdf = " <<
		    _kpdf << " _val = " << _val << "): got " << tmp2 << " for "
		    "_val - are you trying to divide something by zero?!" << std::endl;
		// break return value deliberately
		return (_cval = std::numeric_limits<Double_t>::quiet_NaN());
	    } else if (0. == tmp2) {
		// bin cannot contribute, so that's fine...
		continue;
	    }
	    _cval += tmp1 * tmp2 * bincentre;
	}
    }
    return _cval;
}


//////////////////
// RooSimultaneousResModel //
//////////////////

RooSimultaneousResModel::RooSimultaneousResModel(const char *name, const char *title,
	RooResolutionModel& res_model,
	RooHistPdf& kfactor_pdf,
	RooAbsRealLValue& kfactor_var,
	const RooArgSet& substTargets,
	const RooArgSet& evalInterpVars) :
    RooResolutionModel(name, title, res_model.convVar()),
    _resmodel("resmodel", "resolution model", this, res_model),
    _kfactor_pdf("kfactor_pdf", "k-factor distribution", this, kfactor_pdf),
    _kfactor_var("kfactor_var", "k-factor variable", this, kfactor_var),
    _substTargets("substTargets", "substitution targets", this),
    _evalInterpVars("evalInterpVars", "variables in which to interpolate", this),
    _interpolation("interpolation", "interpolation for use in evaluate()",
	    this, kTRUE, kFALSE, kTRUE),
    _cacheMgr(this)
{
    _substTargets.add(substTargets);
    _evalInterpVars.add(evalInterpVars);
}

RooSimultaneousResModel::RooSimultaneousResModel(const RooSimultaneousResModel& other, const char* name) :
    RooResolutionModel(other, name),
    _resmodel("resmodel", this, other._resmodel),
    _kfactor_pdf("kfactor_pdf", this, other._kfactor_pdf),
    _kfactor_var("kfactor_var", this, other._kfactor_var),
    _substTargets("substTargets", this, other._substTargets),
    _evalInterpVars("evalInterpVars", this, other._evalInterpVars),
    _interpolation("interpolation", "interpolation for use in evaluate()",
	    this, kTRUE, kFALSE, kTRUE),
    _cacheMgr(other._cacheMgr, this)
{
}

RooSimultaneousResModel::~RooSimultaneousResModel()
{ 
}

TObject* RooSimultaneousResModel::clone(const char* newname) const
{ return new RooSimultaneousResModel(*this, newname); }

Int_t RooSimultaneousResModel::basisCode(const char* name) const
{ return resmodel().basisCode(name); }

const RooResolutionModel& RooSimultaneousResModel::resmodel() const
{ return dynamic_cast<RooResolutionModel&>(*_resmodel.absArg()); }

const RooHistPdf& RooSimultaneousResModel::kpdf() const
{ return dynamic_cast<RooHistPdf&>(*_kfactor_pdf.absArg()); }

const RooAbsRealLValue& RooSimultaneousResModel::kvar() const
{ return dynamic_cast<RooAbsRealLValue&>(*_kfactor_var.absArg()); }

Double_t RooSimultaneousResModel::evaluate() const
{
    if (!_evalInterpVars.getSize()) {
	// if we're not interpolating, we get the cache element and evaluate
	// that
	DeceptiveCache *cache = getCache(&s_emptyset, 0);
	assert(cache);
	return cache->getVal();
    } else {
	// ok, we are to interpolate...
	if (!_interpolation.absArg()) {
	    // interpolation object not valid, so create one
	    // first, clone ourselves, but disable the interpolation in the
	    // clone
	    RooSimultaneousResModel* tmp = new RooSimultaneousResModel(*this,
		    (std::string(GetName()) + "_interpolation_source").c_str());
	    assert(tmp);
	    // second, disable interpolation in the clone in tmp
	    tmp->_evalInterpVars.removeAll();
	    // third, create interpolation object
	    RooCachedReal *cache = new RooCachedReal(
		    (std::string(GetName()) + "_interpolation").c_str(),
		    GetTitle(), *tmp, _evalInterpVars);
	    assert(cache);
	    cache->setInterpolationOrder(2);
	    cache->addOwnedComponents(RooArgSet(*tmp));
	    cache->setCacheSource(kTRUE);
	    if (ADirty == tmp->operMode())
		cache->setOperMode(ADirty);
	    // _interpolation owns its contents
	    _interpolation.setArg(*cache);
	}
	return Double_t(_interpolation);
    }
}

RooSimultaneousResModel* RooSimultaneousResModel::convolution(RooFormulaVar* inBasis,
	RooAbsArg* owner) const
{
    // Instantiate a clone of this resolution model representing a
    // convolution with given basis function. The owners object name
    // is incorporated in the clones name to avoid multiple
    // convolution objects with the same name in complex PDF
    // structures.
    //
    // Note: The 'inBasis' formula expression must be a RooFormulaVar
    // that encodes the formula in the title of the object and this
    // expression must be an exact match against the implemented basis
    // function strings (see derived class implementation of method
    // basisCode() for those strings

    // Check that primary variable of basis functions is our convolution variable
    if (inBasis->getParameter(0) != x.absArg()) {
	coutE(InputArguments) << "RooSimultaneousResModel::convolution("
	    << GetName() << "," << this
	    << ") convolution parameter of basis function and PDF don't match"
	    << std::endl << "basis->findServer(0) = "
	    << inBasis->findServer(0) << std::endl
	    << "x.absArg()           = "
	    << x.absArg() << std::endl;
	return 0;
    }

    if (basisCode(inBasis->GetTitle())==0) {
	coutE(InputArguments) << "RooSimultaneousResModel::convolution("
	    << GetName() << "," << this
	    << ") basis function '"
	    << inBasis->GetTitle()
	    << "' is not supported." << std::endl;
	return 0;
    }

    std::string newName(GetName());
    newName += "_conv_";
    newName += inBasis->GetName();
    newName += "_[";
    newName += owner->GetName();
    newName += "]";

    RooResolutionModel *conv = resmodel().convolution(inBasis, owner);

    std::string newTitle(conv->GetTitle());
    newTitle += " convoluted with basis function ";
    newTitle += inBasis->GetName();
    conv->SetTitle(newTitle.c_str());

    RooSimultaneousResModel *kfactor_conv =
	new RooSimultaneousResModel(newName.c_str(), newTitle.c_str(), *conv,
		const_cast<RooHistPdf&>(kpdf()),
		const_cast<RooAbsRealLValue&>(kvar()),
		static_cast<const RooArgSet&>(_substTargets),
		static_cast<const RooArgSet&>(_evalInterpVars));
    kfactor_conv->addOwnedComponents(*conv);
    kfactor_conv->changeBasis(inBasis);

    // interpolation
    const char* cacheParamsStr = getStringAttribute("CACHEPARAMINT");
    if (cacheParamsStr && std::strlen(cacheParamsStr)) {
	kfactor_conv->setStringAttribute("CACHEPARAMINT", cacheParamsStr);
    }

    return kfactor_conv;
}

Int_t RooSimultaneousResModel::getAnalyticalIntegral(RooArgSet& allVars,
	RooArgSet& analVars,
	const char* rangeName) const
{
    if (_forceNumInt) return 0;
    analVars.add(allVars);
    getCache(&allVars, RooNameReg::ptr(rangeName));
    return 1 + _cacheMgr.lastIndex();
}

Double_t RooSimultaneousResModel::analyticalIntegral(Int_t code,
	const char* rangeName) const
{
    assert(code > 0);
    DeceptiveCache* cache =
	static_cast<DeceptiveCache*>(_cacheMgr.getObjByIndex(code - 1));
    if (!cache) {
	std::auto_ptr<RooArgSet> vars(getParameters(RooArgSet()));
	std::auto_ptr<RooArgSet>
	    iset(_cacheMgr.nameSet2ByIndex(code - 1)->select(*vars));
	cache = getCache(iset.get(), RooNameReg::ptr(rangeName));
	assert(cache);
    }
    return cache->getVal();
}

Bool_t RooSimultaneousResModel::forceAnalyticalInt(const RooAbsArg& /*dep*/) const
{ return true; }

RooSimultaneousResModel::DeceptiveCache* RooSimultaneousResModel::getCache(const RooArgSet *iset,
	const TNamed *rangeName) const
{
    int sterileIndex(-1);
    DeceptiveCache* cache = static_cast<DeceptiveCache*>
	(_cacheMgr.getObj(0, iset, &sterileIndex, rangeName));
    // if we have the DeceptiveCache in the cache manager, we return
    if (cache) return cache;
    // if not, we create it...
    cache = new DeceptiveCache(*this, *iset,
	    RooNameReg::str(rangeName));
    assert(cache);
    _cacheMgr.setObj(0, iset, cache, rangeName);
    // and then we call getCache again so that _cacheMgr.lastIndex() returns
    // the right index...
    return getCache(iset, rangeName);
}
