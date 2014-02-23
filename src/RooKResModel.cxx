/**
 * @file   RooKResModel.cxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Fri Aug 30 15:19:15 2013
 *
 * @brief  Implementation file for RooKResModel.
 *
 */

//////////////////////////////////////////////////////////////////////////////
//
// BEGIN_HTML
// Class RooKResModel implements a RooResolutionModel that models an
// internal k-factor correction for other resolution models.  Object
// of class RooKResModel can be used for analytical convolutions with
// classes inheriting from RooAbsAnaConvPdf
// END_HTML
//

#include <cstring>
#include <cstdlib>
#include <cmath>
#include <string>
#include <memory>
#include <limits>
#include <cassert>
#include <sstream>

#include "RooProduct.h"
#include "RooCustomizer.h"
#include "RooFormulaVar.h"
#include "RooNameSet.h"
#include "RooHistPdf.h"
#include "RooRealVar.h"
#include "RooCachedReal.h"

// code injection into RooAbsAnaConvPdf.h: make RooKResModel RooAbsAnaConvPdf's
// friend
#define changeModel(x) changeModel(x); friend class RooKResModel
#include "RooAbsAnaConvPdf.h"
#undef changeModel

#include "B2DXFitters/RooKResModel.h"
#include "B2DXFitters/RooKConvGenContext.h"
#include "RooTruthModel.h"

#include "TPad.h"
#include "RooPlot.h"

RooArgSet RooKResModel::s_emptyset;

///////////////////////////////////
// DeceptiveCache implementation //
///////////////////////////////////

RooKResModel::DeceptiveCache::DeceptiveCache(const RooKResModel& parent,
	const RooArgSet& iset,
	const char* rangeName) :
    _cval(std::numeric_limits<double>::quiet_NaN()),
    _kvar(0), _kpdf(0), _val(0), _parent(parent)
{
    // build a (hopefully unique) suffix for objects we have to clone/modify
    std::ostringstream os;
    os << "DeceptiveCache_" << parent.GetName() << "_" <<
	reinterpret_cast<void*>(this);
    if (0 < iset.getSize()) {
       	os << "_" << RooNameSet(iset).content();
    }
    if (rangeName && std::strlen(rangeName)) {
	    os << "_" << rangeName;
    }
    const std::string sfx = os.str();

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

    _kvar = dynamic_cast<RooRealVar*>(kvar.clone(
		(std::string(kvar.GetName()) + "_" + sfx).c_str()));
    assert(_kvar);
    _knset.add(*_kvar);
    {
	RooCustomizer c(kpdf, sfx.c_str());
	c.replaceArg(kvar, *_kvar);
	_kpdf = dynamic_cast<RooHistPdf*>(c.build());
    }

    RooAbsReal* cache = 0;

    // customise resolution model
    {
	// for some reason, RooCustomizer below doesn't always clone the
	// object, so we do it explicitly
	RooAbsArg* tmpresmodel = dynamic_cast<RooAbsArg*>(
		parent.resmodel().clone(
		    (std::string(parent.resmodel().GetName()) + sfx).c_str()));
	assert(tmpresmodel);
	RooCustomizer c(*tmpresmodel, sfx.c_str());
	// get list of terms t in resmodel that may need replacement t -> k * t
	RooArgSet params;
	parent.resmodel().treeNodeServerList(&params);

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
	cache = dynamic_cast<RooAbsReal*>(c.build());
	assert(cache);
	if (cache != tmpresmodel) new_paramset.add(*tmpresmodel);
	cache->addOwnedComponents(new_paramset); // new resmodel owns params (k*old)
    }

    // check if we need to integrate
    if (0 < iset.getSize()) {
	_val = cache->createIntegral(iset, rangeName);
	assert(_val);
	_val->addOwnedComponents(RooArgSet(*cache));
    } else {
	_val = cache;
    }
    _val->setValueDirty();
    _val->setShapeDirty();
}

RooKResModel::DeceptiveCache::DeceptiveCache(const RooKResModel& parent) :
    _cval(std::numeric_limits<double>::quiet_NaN()),
    _kvar(0), _kpdf(0), _val(0), _parent(parent)
{
    // interpolation object not valid, so create one
    // first, clone ourselves, but disable the interpolation in the
    // clone
    std::ostringstream os;
    os << parent.GetName() << "_" << this << "_interpolation";
    RooKResModel* tmp = dynamic_cast<RooKResModel*>(parent.clone(
		(os.str() + "_source").c_str()));
    assert(tmp);
    tmp->_evalInterpVars.removeAll();
    // create interpolation object
    RooCachedReal *ecache = new RooCachedReal(os.str().c_str(),
	    parent.GetTitle(), *tmp, parent._evalInterpVars);
    assert(ecache);
    ecache->addOwnedComponents(RooArgSet(*tmp));
    ecache->setInterpolationOrder(2);
    ecache->setCacheSource(kFALSE);
    if (ADirty == tmp->operMode())
	ecache->setOperMode(ADirty);

    _val = ecache;
}

RooKResModel::DeceptiveCache::~DeceptiveCache()
{
    _knset.removeAll();
    delete _val;
    delete _kpdf;
    delete _kvar;
    _val = 0, _kpdf = 0, _kvar = 0;
}

RooArgList RooKResModel::DeceptiveCache::containedArgs(RooAbsCacheElement::Action)
{
    // Return list of all RooAbsArgs in cache element
    if (!_kpdf) return RooArgList(*_val);
    return RooArgList(*_val, *_kpdf, *_kvar);
}

double RooKResModel::DeceptiveCache::getVal(const RooArgSet* nset) const
{
    if (!_kpdf) return _val->getVal(nset);
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
// RooKResModel //
//////////////////

RooKResModel::RooKResModel()
{ }

RooKResModel::RooKResModel(const char *name, const char *title,
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
    _cacheMgr(this)
{
    _substTargets.add(substTargets);
    _evalInterpVars.add(evalInterpVars);
}

RooKResModel::RooKResModel(const RooKResModel& other, const char* name) :
    RooResolutionModel(other, name),
    _resmodel("resmodel", this, other._resmodel),
    _kfactor_pdf("kfactor_pdf", this, other._kfactor_pdf),
    _kfactor_var("kfactor_var", this, other._kfactor_var),
    _substTargets("substTargets", this, other._substTargets),
    _evalInterpVars("evalInterpVars", this, other._evalInterpVars),
    _cacheMgr(other._cacheMgr, this)
{ }

RooKResModel::~RooKResModel()
{ }

TObject* RooKResModel::clone(const char* newname) const
{ return new RooKResModel(*this, newname); }

Int_t RooKResModel::basisCode(const char* name) const
{ return resmodel().basisCode(name); }

const RooResolutionModel& RooKResModel::resmodel() const
{ return dynamic_cast<RooResolutionModel&>(*_resmodel.absArg()); }

const RooHistPdf& RooKResModel::kpdf() const
{ return dynamic_cast<RooHistPdf&>(*_kfactor_pdf.absArg()); }

const RooAbsRealLValue& RooKResModel::kvar() const
{ return dynamic_cast<RooAbsRealLValue&>(*_kfactor_var.absArg()); }

Double_t RooKResModel::evaluate() const
{
    const bool interpolate = 0 < _evalInterpVars.getSize();
    DeceptiveCache *cache = getCache(&s_emptyset, 0, interpolate);
    assert(cache);
    return cache->getVal(0);
}

RooKResModel* RooKResModel::convolution(RooFormulaVar* inBasis,
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
	coutE(InputArguments) << "RooKResModel::convolution("
	    << GetName() << "," << this
	    << ") convolution parameter of basis function and PDF don't match"
	    << std::endl << "basis->findServer(0) = "
	    << inBasis->findServer(0) << std::endl
	    << "x.absArg()           = "
	    << x.absArg() << std::endl;
	return 0;
    }

    if (basisCode(inBasis->GetTitle())==0) {
	coutE(InputArguments) << "RooKResModel::convolution("
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
    assert(conv);

    std::string newTitle(conv->GetTitle());
    newTitle += " convoluted with basis function ";
    newTitle += inBasis->GetName();
    conv->SetTitle(newTitle.c_str());

    RooKResModel *kfactor_conv =
	new RooKResModel(newName.c_str(), newTitle.c_str(), *conv,
		const_cast<RooHistPdf&>(kpdf()),
		const_cast<RooAbsRealLValue&>(kvar()),
		static_cast<const RooArgSet&>(_substTargets),
		static_cast<const RooArgSet&>(_evalInterpVars));
    assert(kfactor_conv);
    kfactor_conv->changeBasis(inBasis);
    kfactor_conv->addOwnedComponents(*conv);

    // interpolation
    const char* cacheParamsStr = getStringAttribute("CACHEPARAMINT");
    if (cacheParamsStr && std::strlen(cacheParamsStr)) {
	kfactor_conv->setStringAttribute("CACHEPARAMINT", cacheParamsStr);
    }

    return kfactor_conv;
}

Int_t RooKResModel::getAnalyticalIntegral(RooArgSet& allVars,
	RooArgSet& analVars, const char* rangeName) const
{
    if (_forceNumInt) return 0;
    analVars.add(allVars);
    getCache(&allVars, RooNameReg::ptr(rangeName));
    return 1 + _cacheMgr.lastIndex();
}

Double_t RooKResModel::analyticalIntegral(Int_t code,
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

Bool_t RooKResModel::forceAnalyticalInt(const RooAbsArg& /*dep*/) const
{ return true; }

RooKResModel::DeceptiveCache* RooKResModel::getCache(const RooArgSet *iset,
	const TNamed *rangeName, bool interp) const
{
    int sterileIndex(-1);
    DeceptiveCache* cache = static_cast<DeceptiveCache*>
	(_cacheMgr.getObj(0, iset, &sterileIndex, rangeName));
    // if we have the DeceptiveCache in the cache manager, we return
    if (cache) return cache;
    // if not, we create it...
    if (interp) {
	assert(!iset || !iset->getSize());
	cache = new DeceptiveCache(*this);
    } else {
	cache = new DeceptiveCache(*this, *iset, RooNameReg::str(rangeName));
    }
    assert(cache);
    _cacheMgr.setObj(0, iset, cache, rangeName);
    // and then we call getCache again so that _cacheMgr.lastIndex() returns
    // the right index...
    return getCache(iset, rangeName, interp);
}

RooAbsGenContext* RooKResModel::modelGenContext(
	const RooAbsAnaConvPdf& convPdf, const RooArgSet &vars,
	const RooDataSet *prototype, const RooArgSet* auxProto,
	Bool_t verbose) const                                                                                                                                                                 
{
    std::string kname(kvar().GetName());
    kname += "_GenContext";
    // clone the k-factor variable
    RooRealVar* newkvar = dynamic_cast<RooRealVar*>(
	    kvar().clone(kname.c_str()));
    assert(newkvar);
    // get k-factor distribution in terms of new variable
    RooAbsPdf* newkpdf = 0;
    {
	RooCustomizer c(kpdf(), "GenContext");
	c.replaceArg(kvar(), *newkvar);
	newkpdf = dynamic_cast<RooAbsPdf*>(c.build());
	assert(newkpdf);
    }

    RooAbsAnaConvPdf *newpdf = 0, *tmppdf = 0;
    {
	// get pdf in terms of underlying resolution model
	std::string pdfname(convPdf.GetName());
	pdfname += "_GenContext";
	tmppdf = dynamic_cast<RooAbsAnaConvPdf*>(
		convPdf.clone(pdfname.c_str()));
	assert(tmppdf);
	const RooResolutionModel& resmodel_t =
	    dynamic_cast<const RooResolutionModel&>(_resmodel.arg());
	std::string resmodelname(resmodel_t.GetName());
	resmodelname += "_GenContext";
	RooResolutionModel* newresmodel = dynamic_cast<RooResolutionModel*>(
		resmodel_t.clone(resmodelname.c_str()));
	newresmodel->changeBasis(0);
	tmppdf->changeModel(*newresmodel);
	// substitute q -> k * q for all q in _substTargets
	RooCustomizer c(*tmppdf, "GenContext");
	RooArgSet params;
	convPdf.treeNodeServerList(&params);
	RooArgSet new_paramset(*newresmodel);
	RooFIter it = params.fwdIterator();
	for (RooAbsArg* param = it.next(); param; param = it.next()) {
	    if (!_substTargets.find(*param)) continue;
	    std::string parname(param->GetName());
	    parname += "_x_"; parname += newkvar->GetName();
	    RooProduct *new_param = new RooProduct(parname.c_str(), parname.c_str(),
		    RooArgList(*param, *newkvar));
	    assert(new_param);
	    c.replaceArg(*param, *new_param);
	    new_paramset.add(*new_param);
	}
	newpdf = dynamic_cast<RooAbsAnaConvPdf*>(c.build());
	assert(newpdf);
	// make sure we do not leak
	newpdf->addOwnedComponents(new_paramset);
	// clean up the temporaries
    }

    // get a context for the underlying pdf with k-factors substituted in
    RooAbsGenContext* retVal = new RooKConvGenContext(
    	    *newpdf, *newkvar, *newkpdf, vars, prototype, auxProto, verbose);
    assert(retVal);
    delete tmppdf;
    // clean up the temporaries
    delete newpdf;
    delete newkpdf;
    delete newkvar;

    return retVal;
}

Bool_t RooKResModel::isDirectGenSafe(const RooAbsArg& arg) const
{
    bool retVal = (!std::strcmp(x.arg().GetName(), arg.GetName()) ||
	RooResolutionModel::isDirectGenSafe(arg)) &&
	dynamic_cast<const RooAbsPdf&>(_resmodel.arg()).isDirectGenSafe(arg);
    return retVal;
}

Int_t RooKResModel::getGenerator(const RooArgSet& directVars,
	RooArgSet &generateVars, Bool_t staticInitOK) const
{
    Int_t code = dynamic_cast<const RooAbsPdf&>(_resmodel.arg()).getGenerator(
	    directVars, generateVars, staticInitOK);
    return code;
}

void RooKResModel::generateEvent(Int_t /* code */)
{
    // this should never be called in proper operation
    std::abort();
}

