{
    'Debug': True,
    'UseKFactor': False,
    'ParameteriseIntegral': True,

    'FitConfig': {
        'Optimize': 1,
        'Offset': True,
        'NumCPU': 1,
        'Strategy': 2,
    },

    'IsData': False,
    'Blinding': True,

    'DecayTimeResolutionModel': 'GaussianWithPEDTE', # per event decay time error
    'DecayTimeResolutionBias': 0., # if there is a shift
    'DecayTimeResolutionScaleFactor': 1.0, # usually the errors need a bit of scaling
    'DecayTimeResolutionAvg': 0.40, # average decay time resolution

    'AcceptanceFunction': 'Spline',
    'SplineAcceptance': { # configure spline acceptance parameters
        'KnotPositions':    [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
        'KnotCoefficients': { # different between generation and fit
            'GEN': [ 4.5853e-01, 6.8963e-01, 8.8528e-01,
                     1.1296e+00, 1.2232e+00, 1.2277e+00 ],
            'FIT': [ 4.5853e-01, 6.8963e-01, 8.8528e-01,
                     1.1296e+00, 1.2232e+00, 1.2277e+00 ],
            },
        },

    # dummy shape for easy testing in toys:
    #  ^              * zero from omega=0 to omega0
    #  |      *  |    * quadratic rise starting at omega0
    #  |     * * |    * turning point omega_c calculated
    #  |    *   *|      to match desired average omega
    #  |  **     * f  * from there, linear down to point (0.5, f)
    #  ***-------+
    #  0 omega0  0.5
    'TrivialMistagParams': {
        'omegaavg': 0.350, # desired expectation value of mistag distribution
        'omega0': 0.07, # start quadratic increase at omega0
        'f': 0.25, # final point P(0.5) = f
        },
    'MistagCalibParams': { # tagging calibration parameters
        'p0':     0.345,
        'p1':     0.980,
        'etaavg': 0.350
        },

    'constParams': [
        '.*_scalefactor', # anything ending in '_scalefactor'...
        'Bs2DsPi_accpetance_SplineAccCoeff[0-9]+', # spline acceptance fixed
        ],

    'NBinsAcceptance': 100,
    'NBinsProperTimeErr': 100,
}
