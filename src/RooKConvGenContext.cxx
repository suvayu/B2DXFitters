/*****************************************************************************
 * Project: RooFit                                                           *
 * Package: RooFitCore                                                       *
 * @(#)root/roofitcore:$Id$
 * Authors:                                                                  *
 *   WV, Wouter Verkerke, UC Santa Barbara, verkerke@slac.stanford.edu       *
 *   DK, David Kirkby,    UC Irvine,         dkirkby@uci.edu                 *
 *                                                                           *
 * Copyright (c) 2000-2005, Regents of the University of California          *
 *                          and Stanford University. All rights reserved.    *
 *                                                                           *
 * Redistribution and use in source and binary forms,                        *
 * with or without modification, are permitted according to the terms        *
 * listed in LICENSE (http://roofit.sourceforge.net/license.txt)             *
 *****************************************************************************/

//////////////////////////////////////////////////////////////////////////////
//
// BEGIN_HTML
// RooKConvGenContext is an efficient implementation of the generator context
// specific for RooAbsAnaConvPdf objects. The physics model is generated
// with a truth resolution model and the requested resolution model is generated
// separately as a PDF. The convolution variable of the physics model is
// subsequently explicitly smeared with the resolution model distribution.
// END_HTML
//

#include "RooFit.h"

#include "RooMsgService.h"
#include "RooDataSet.h"
#include "RooArgSet.h"
#include "Riostream.h"

// code injection into RooAbsAnaConvPdf.h: make RooKConvGenContext
// RooAbsAnaConvPdf's friend
#define changeModel(x) changeModel(x); friend class RooKConvGenContext
// code injection into RooAbsPdf.h: make RooKConvGenContext RooAbsPdf's friend
#define RooEffGenContext RooEffGenContext; friend class RooKConvGenContext
#include "RooAbsAnaConvPdf.h"
#undef changeModel
#undef RooEffGenContext

#include "RooRealVar.h"

#include "B2DXFitters/RooKConvGenContext.h"

using namespace std;


//_____________________________________________________________________________
RooKConvGenContext::RooKConvGenContext(
	const RooAbsAnaConvPdf& model,
	const RooAbsRealLValue& kvar, const RooAbsPdf& kpdf,
	const RooArgSet& vars, const RooDataSet* prototype,
	const RooArgSet* auxProto, Bool_t verbose) :
    RooAbsGenContext(model,vars,prototype,auxProto,verbose), _pdfVarsOwned(0), _modelVarsOwned(0)
{
    // Constructor for specialized generator context for analytical convolutions.
    //
    // Builds a generator for the physics PDF convoluted with the truth model
    // and a generator for the resolution model as PDF. Events are generated
    // by sampling events from the p.d.f and smearings from the resolution model
    // and adding these to obtain a distribution of events consistent with the
    // convolution of these two. The advantage of this procedure is so that
    // both p.d.f and resolution model can take advantage of any internal
    // generators that may be defined.

    cxcoutI(Generation) << "RooKConvGenContext::ctor() setting up special generator context for analytical convolution p.d.f. " << model.GetName()
	<< " for generation of observable(s) " << vars << endl;

    // Clone resolution model and use as normal PDF
    _modelCloneSet = (RooArgSet*) RooArgSet(kpdf).snapshot(kTRUE);
    if (!_modelCloneSet) {
	coutE(Generation) << "RooKConvGenContext::RooKConvGenContext(" << GetName() << ") Couldn't deep-clone k-factor distribution, abort," << endl;
	RooErrorHandler::softAbort();
    }
    RooAbsPdf* modelClone = (RooAbsPdf*) _modelCloneSet->find(kpdf.GetName());
    RooAbsRealLValue* kvarClone = (RooAbsRealLValue*) _modelCloneSet->find(kvar.GetName());
    // Create generator for resolution model as PDF
    _modelVars = (RooArgSet*) modelClone->getObservables(&vars);

    _modelVars->add(*kvarClone);
    _kVarName = kvarClone->GetName();
    _modelGen = modelClone->genContext(*_modelVars,prototype,auxProto,verbose);

    // Clone PDF and change model to internal truth model
    _pdfCloneSet = (RooArgSet*) RooArgSet(model).snapshot(kTRUE);
    if (!_pdfCloneSet) {
	coutE(Generation) << "RooKConvGenContext::RooKConvGenContext(" << GetName() << ") Couldn't deep-clone PDF, abort," << endl;
	RooErrorHandler::softAbort();
    }

    RooAbsAnaConvPdf* pdfClone = (RooAbsAnaConvPdf*) _pdfCloneSet->find(model.GetName());
    _convVarName = pdfClone->convVar()->GetName();

    // Create generator for physics X truth model
    _pdfVars = (RooArgSet*) pdfClone->getObservables(&vars);
    RooArgSet tmpauxProto;
    if (auxProto) tmpauxProto.add(*auxProto);
    tmpauxProto.add(*kvarClone);
    _pdfGen = pdfClone->genContext(*_pdfVars,prototype,&tmpauxProto,verbose);

    if (prototype) {
	_pdfVars->add(*prototype->get());
	_modelVars->add(*prototype->get());
    }

    // WVE ADD FOR DEBUGGING
    _pdfVars->add(tmpauxProto);
    if (auxProto) {
        _modelVars->add(*auxProto);
    }

//   cout << "RooKConvGenContext::ctor(" << this << "," << GetName() << ") _pdfVars = " << _pdfVars << " "; _pdfVars->Print("1");
//   cout << "RooKConvGenContext::ctor(" << this << "," << GetName() << ") _modelVars = " << _modelVars << " "; _modelVars->Print("1");
}

//_____________________________________________________________________________
RooKConvGenContext::~RooKConvGenContext()
{
    // Destructor

    // Destructor. Delete all owned subgenerator contexts
    delete _pdfGen;
    delete _modelGen;
    delete _pdfCloneSet;
    delete _modelCloneSet;
    delete _modelVars;
    delete _pdfVars;
    delete _pdfVarsOwned;
    delete _modelVarsOwned;
}



//_____________________________________________________________________________
void RooKConvGenContext::attach(const RooArgSet& args)
{
    // Attach given set of arguments to internal clones of
    // pdf and resolution model

    // Find convolution variable in input and output sets
    RooRealVar* cvModel = (RooRealVar*) _modelVars->find(_convVarName);
    RooRealVar* cvPdf   = (RooRealVar*) _pdfVars->find(_convVarName);

    // Replace all servers in _pdfVars and _modelVars with those in theEvent, except for the convolution variable
    RooArgSet* pdfCommon = (RooArgSet*) args.selectCommon(*_pdfVars);
    pdfCommon->remove(*cvPdf,kTRUE,kTRUE);

    RooArgSet* modelCommon = (RooArgSet*) args.selectCommon(*_modelVars);
    modelCommon->remove(*cvModel,kTRUE,kTRUE);

    _modelGen->attach(*modelCommon);
    _pdfGen->attach(*pdfCommon);

    delete pdfCommon;
    delete modelCommon;
}


//_____________________________________________________________________________
void RooKConvGenContext::initGenerator(const RooArgSet& theEvent)
{
    // One-time initialization of generator context, attaches
    // the context to the supplied event container

    // Find convolution variable in input and output sets
    _cvModel = (RooRealVar*) _modelVars->find(_kVarName);
    _cvPdf   = (RooRealVar*) _pdfVars->find(_convVarName);
    _cvOut   = (RooRealVar*) theEvent.find(_convVarName);

    // Replace all servers in _pdfVars and _modelVars with those in theEvent, except for the convolution variable
    RooArgSet* pdfCommon = (RooArgSet*) theEvent.selectCommon(*_pdfVars);
    if (_cvPdf) pdfCommon->remove(*_cvPdf,kTRUE,kTRUE);
    _pdfVars->replace(*pdfCommon);
    delete pdfCommon;

    RooArgSet* modelCommon = (RooArgSet*) theEvent.selectCommon(*_modelVars);
    if (_cvModel) modelCommon->remove(*_cvModel,kTRUE,kTRUE);
    _modelVars->replace(*modelCommon);
    delete modelCommon;

    // Initialize component generators
    _modelGen->initGenerator(*_modelVars);
    _pdfGen->initGenerator(*_pdfVars);
}



//_____________________________________________________________________________
void RooKConvGenContext::generateEvent(RooArgSet& theEvent, Int_t remaining)
{
    // Generate a single event
    do {
        // generate a value for kvar
	do {
	    _modelGen->generateEvent(*_modelVars,remaining);
	} while (!_cvModel->isValidReal(_cvModel->getVal()));
	// generate the rest of the pdf
        _pdfGen->generateEvent(*_pdfVars,remaining);
    } while (!_cvOut->isValidReal(_cvPdf->getVal()));
    // Smeared value in acceptance range, transfer values to output set
    theEvent = *_pdfVars;
}



//_____________________________________________________________________________
void RooKConvGenContext::setProtoDataOrder(Int_t* lut)
{
    // Set the traversal order for events in the prototype dataset
    // The argument is a array of integers with a size identical
    // to the number of events in the prototype dataset. Each element
    // should contain an integer in the range 1-N.

    RooAbsGenContext::setProtoDataOrder(lut);
    _modelGen->setProtoDataOrder(lut);
    _pdfGen->setProtoDataOrder(lut);
}


//_____________________________________________________________________________
void RooKConvGenContext::printMultiline(ostream& os, Int_t content, Bool_t verbose, TString indent) const
{
    // Print the details of this generator context

    RooAbsGenContext::printMultiline(os,content,verbose,indent);
    os << indent << "--- RooKConvGenContext ---" << endl;
    os << indent << "List of component generators" << endl;

    TString indent2(indent);
    indent2.Append("    ");

    _modelGen->printMultiline(os,content,verbose,indent2);
    _pdfGen->printMultiline(os,content,verbose,indent2);
}
