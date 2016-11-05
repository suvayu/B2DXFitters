"""
@file resmodelutils.py

@author Manuel Schiller <Manuel.Schiller@cern.ch>
@date 2015-06-11

@brief utilities to build resolution models
"""
import ROOT
from B2DXFitters.WS import WS as WS

def getResolutionModel(
        ws,             # workspace
        config,         # config dictionary
        time,           # time observable
        timeerr,        # time error observable (if applicable)
        tacc            # acceptance (if applicable)
        ):
    """
    obtain specified resolution model

    ws      -- workspace into which to import resolution model
    config  -- config dictionary with settings (see below for relevant keys)
    time    -- time observable
    timeerr -- time error observable (or None, if average time error is used)
    tacc    -- time acceptance

    returns tuple of resolution model (possibly acceptance corrected) and
    acceptance

    The logic here is:
    - for fitting, and with a spline acceptance, the acceptance becomes part
      of the resolution model for technical reasons; therefore, the routine
      should return the appropriate pair of resolution model including
      acceptance and a dummy acceptance (to avoid double-correcting) to use in
      buildBDecayTimePdf
    - for generation, it is more efficient computationally to keep acceptance
      and resolution model separate, the routine thus does that

    relevant config dictionary entries:
    'DecayTimeResolutionModel':
        can be either of:
        - 'GaussianWithPEDTE': a single gaussian resolution model with per
          event decay time errors
        - a dictionary { 'sigmas': [ sigma_0, sigma_1, ..., sigma_N],
          'fractions': [ f_0, ..., f_{N - 1} ] }; this specifies an average
          resolution as a superposition of Gaussians with common mean and
          different widths and fractions
        - a list/tuple of [ [sigma_0, sigma_1, ..., sigma_N], [f_0, ...,
          f_{N-1} ] ]; this also specifies an average resolution as a
          superposition of Gaussians with common mean and different widths and
          fractions
    'DecayTimeResolutionBias':
        common mean/bias of (superposition of) Gaussian(s)
    'DecayTimeResolutionScaleFactor':
        scale factor to apply to given resolution model (as in
        time error -> time error * S)
    'Context':
        if the string in config['Context'] contains "GEN", the generation
        version of the resolution model is produces (where resolution and
        acceptance are kept strictly separate, as is most efficient for
        generation); otherwise a fitting context is assumed, and an
        acceptance-corrected resolution model is returned if a spline
        acceptance function is used
    'Acceptance':
        if equal to "Spline", and if config['Context'] indicates a fit job
        (and not a generation job), the appropriate spline-acceptance-
        corrected resolution model is returned
    """
    tacc_name = 'None' if None == tacc else tacc.GetName()
    if (type(config['DecayTimeResolutionModel']) == list or
            type(config['DecayTimeResolutionModel']) == tuple or
            type(config['DecayTimeResolutionModel']) == dict):
        print "=>resmodelutils.getResolutionModel(): using list/tuple/dict to build resolution."
        if (type(config['DecayTimeResolutionModel']) == dict):
            sigmas = config['DecayTimeResolutionModel']['sigmas']
            fractions = config['DecayTimeResolutionModel']['fractions']
            ncomp = len(sigmas)
            if (len(fractions) + 1 != len(sigmas)):
                raise TypeError('Unknown type of resolution model')
        else:
            # ok, we got a list of: [sigma_0,sigma_1, ...] and [f0,f1,...]
            # build specified resolution model on the fly
            if 2 != len(config['DecayTimeResolutionModel']):
                raise TypeError('Unknown type of resolution model')
            ncomp = len(config['DecayTimeResolutionModel'][0])
            if ncomp < 1:
                raise TypeError('Unknown type of resolution model')
            if ncomp != len(config['DecayTimeResolutionModel'][1]) and \
                    ncomp - 1 != len(config['DecayTimeResolutionModel'][1]):
                raise TypeError('Unknown type of resolution model')
            sigmas = config['DecayTimeResolutionModel'][0]
            fractions = config['DecayTimeResolutionModel'][1]
        from ROOT import ( RooArgList, RooRealVar, RooGaussModel,
                RooGaussEfficiencyModel, RooAddModel )
        pdfs = RooArgList()
        fracs = RooArgList()
        i = 0
        for s in sigmas:
            sigma = WS(ws, RooRealVar('resmodel%02d_sigma' % i,
                'resmodel%02d_sigma' % i, s, 'ps'))
            bias = WS(ws, RooRealVar('timeerr_bias',
                'timeerr_bias', config['DecayTimeResolutionBias']))
            sf = WS(ws, RooRealVar('timeerr_scalefactor',
                'timeerr_scalefactor',
                config['DecayTimeResolutionScaleFactor'], .5, 2.))
            if 'Spline' != config['AcceptanceFunction'] or 'GEN' in config['Context']:
                pdfs.add(WS(ws, RooGaussModel('resmodel%02d' % i, 'resmodel%02d' % i,
                    time, bias, sigma, sf)))
            else:
                # spline acceptance
                print "=>resmodelutils.getResolutionModel(): multiplying resolution by spline acceptance"
                pdfs.add(WS(ws, RooGaussEfficiencyModel(
                    '%s_resmodel%02d' % (tacc_name, i),
                    '%s_resmodel%02d' % (tacc_name, i),
                    time, tacc, bias, sigma, sf, sf)))
            del sf
            del bias
            i += 1
        i = 0
        for s in fractions:
            fracs.add(WS(ws, RooRealVar('resmodel%02d_frac' % i,
                'resmodel%02d_frac' % i, s, 'ps')))
            i += 1
        del s
        del i
        trm = WS(ws, RooAddModel('%s_resmodel' % tacc_name,
            '%s_resmodel' % tacc_name, pdfs, fracs))
        del pdfs
        del fracs
        del ncomp
        if ('Spline' == config['AcceptanceFunction'] and
                not 'GEN' in config['Context']):
            # if we're using a spline acceptance, we're done
            print "=>resmodelutils.getResolutionModel(): using spline acceptance in fitting stage. Returning null acceptance (already included in resolution.)"
            tacc = None
    elif type(config['DecayTimeResolutionModel']) == str:
        print "=>resmodelutils.getResolutionModel(): using per-event time resolution."
        if config['DecayTimeResolutionModel'] != 'GaussianWithPEDTE':
            raise TypeError('Unknown type of resolution model: %s' %
                    config['DecayTimeResolutionModel'])
        from ROOT import RooRealVar, RooGaussModel, RooGaussEfficiencyModel
        # time, mean, timeerr, scale
        bias = WS(ws, RooRealVar('timeerr_bias',
            'timeerr_bias', config['DecayTimeResolutionBias']))
        sf = WS(ws, RooRealVar('timeerr_scalefactor',
            'timeerr_scalefactor',
            config['DecayTimeResolutionScaleFactor'], .5, 2.))
        if ('Spline' != config['AcceptanceFunction'] or
                'GEN' in config['Context']):
            trm = WS(ws, RooGaussModel('GaussianWithPEDTE',
                'GaussianWithPEDTE', time, bias, timeerr, sf))
        else:
            print "=>resmodelutils.getResolutionModel(): multiplying resolution by spline acceptance"
            trm = WS(ws, RooGaussEfficiencyModel(
                '%s_GaussianWithPEDTE' % tacc_name,
                '%s_GaussianWithPEDTE' % tacc_name,
                time, tacc, bias, timeerr, sf, sf))
            # if we're using a spline acceptance, we're done
            print "=>resmodelutils.getResolutionModel(): using spline acceptance in fitting stage. Returning null acceptance (already included in resolution.)"
            tacc = None
        del bias
        del sf
    else:
        raise TypeError('Unknown type of resolution model')
    return trm, tacc

