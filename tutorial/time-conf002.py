{
    'Debug': True,
    'UseKFactor': False,
    'ParameteriseIntegral': False,

    'FitConfig': {
        'Optimize': 1,
        'Offset': True,
        'NumCPU': 1,
        'Strategy': 2,
    },

    'IsData': False,
    'Blinding': True,

    # 40 fs average resolution
    'DecayTimeResolutionModel':  { 'sigmas': [ 0.040, ], 'fractions': [] },
    'DecayTimeResolutionBias': 0., # if there is a shift
    'DecayTimeResolutionScaleFactor': 1.0, # usually the errors need a bit of scaling

    'AcceptanceFunction': 'Spline',
    'SplineAcceptance': { # configure spline acceptance parameters
        'KnotPositions':    [ 0.5, 1.0, 1.5, 2.0, 3.0, 12.0 ],
        'KnotCoefficients': { # different between generation and fit
            'GEN': [ 4.5853e-01, 6.8963e-01, 8.8528e-01,
                     1.1296e+00, 1.2232e+00, 1.2277e+00 ],
            'FIT': [ 0.5, 0.75, 1.0, 1.0, 1.0, 1.0 ],
            },
        },

    'constParams': [
        '.*_scalefactor', # anything ending in '_scalefactor'...
        ],

    'NBinsAcceptance': 100,
}
