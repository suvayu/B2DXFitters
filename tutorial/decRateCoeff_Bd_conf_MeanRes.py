{
    'Debug': True,
    'UseKFactor': False,
    'ParameteriseIntegral': True,
    'UseProtoData': True,

    'FitConfig': {
        'Optimize': 1,
        'Offset': True,
        'NumCPU': 1,
        'Strategy': 2,
    },

    # 50 fs average resolution
    'DecayTimeResolutionModel':  { 'sigmas': [ 0.050, ], 'fractions': [] },
    'DecayTimeResolutionBias': 0., # if there is a shift
    'DecayTimeResolutionScaleFactor': 1.0, # usually the errors need a bit of scaling

    'AcceptanceFunction': 'Spline',
    'SplineAcceptance': { # configure spline acceptance parameters
    'KnotPositions':    [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
    'KnotCoefficients': { # may be different between generation and fit
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

    'NBinsAcceptance' : 0,

    'constParams': [
    '.*_scalefactor', # anything ending in '_scalefactor'...
    ],
}
