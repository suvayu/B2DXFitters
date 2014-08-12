"""Resolution model

"""


from B2DXFitters.WS import WS


def getResolutionModel(
        ws,             # workspace
        config,         # config dictionary
        time,           # time observable
        timeerr,        # time error observable (if applicable)
        tacc            # acceptance (if applicable)
        ):
    if (type(config['DecayTimeResolutionModel']) == list or
    type(config['DecayTimeResolutionModel']) == tuple):
        # ok, we got a list of: [sigma_0,sigma_1, ...] and [f0,f1,...]
        # build specified resolution model on the fly
        from ROOT import ( RooArgList, RooRealVar, RooGaussModel,
                RooGaussEfficiencyModel, RooAddModel )
        if 2 != len(config['DecayTimeResolutionModel']):
            raise TypeError('Unknown type of resolution model')
        ncomp = len(config['DecayTimeResolutionModel'][0])
        if ncomp < 1:
            raise TypeError('Unknown type of resolution model')
        if ncomp != len(config['DecayTimeResolutionModel'][1]) and \
                ncomp - 1 != len(config['DecayTimeResolutionModel'][1]):
            raise TypeError('Unknown type of resolution model')
        pdfs = RooArgList()
        fracs = RooArgList()
        i = 0
        for s in config['DecayTimeResolutionModel'][0]:
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
                pdfs.add(WS(ws, RooGaussEfficiencyModel(
                    '%s_resmodel%02d' % (tacc.GetName(), i),
                    '%s_resmodel%02d' % (tacc.GetName(), i),
                    time, tacc, bias, sigma, sf, sf)))
            del sf
            del bias
            i += 1
        i = 0
        for s in config['DecayTimeResolutionModel'][1]:
            fracs.add(WS(ws, RooRealVar('resmodel%02d_frac' % i,
                'resmodel%02d_frac' % i, s, 'ps')))
            i += 1
        del s
        del i
        trm = WS(ws, RooAddModel('%s_resmodel' % tacc.GetName(),
            '%s_resmodel' % tacc.GetName(), pdfs, fracs))
        del pdfs
        del fracs
        del ncomp
        if ('Spline' == config['AcceptanceFunction'] and
                not 'GEN' in config['Context']):
            # if we're using a spline acceptance, we're done
            tacc = None
    elif type(config['DecayTimeResolutionModel']) == str:
        if 'PEDTE' not in config['DecayTimeResolutionModel']:
            if 'Spline' == config['AcceptanceFunction']:
                print ('ERROR: decay time resolution model %s'
                        'incompatible with spline acceptance') % (
                                config['DecayTimeResolutionModel'])
                return None
            PTResModels = ROOT.PTResModels
            trm = WS(ws, PTResModels.getPTResolutionModel(
                config['DecayTimeResolutionModel'],
                time, 'Bs', debug,
                config['DecayTimeResolutionScaleFactor'],
                config['DecayTimeResolutionBias']))
        else :
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
                trm = WS(ws, RooGaussEfficiencyModel(
                    '%s_GaussianWithPEDTE' % tacc.GetName(),
                    '%s_GaussianWithPEDTE' % tacc.GetName(),
                    time, tacc, bias, timeerr, sf, sf))
                # if we're using a spline acceptance, we're done
                tacc = None
            del bias
            del sf
    else:
        raise TypeError('Unknown type of resolution model')
    return trm, tacc


# speed up the fit by parameterising integrals of the resolution model over
# time in the (per-event) time error (builds a table if integral values and
# interpolates)
def parameteriseResModelIntegrals(config, ws, timeerrpdf, timeerr, timeresmodel):
    if None == timeerrpdf or 0 == config['NBinsProperTimeErr']:
        return
    from ROOT import RooArgSet
    if not timeerr.hasBinning('cache'):
        timeerr.setBins(config['NBinsProperTimeErr'], 'cache')
    timeresmodel.setParameterizeIntegral(RooArgSet(timeerr))
