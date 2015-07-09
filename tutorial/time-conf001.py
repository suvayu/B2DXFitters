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

    'DecayTimeResolutionModel': [ [ 0.040, ], [] ], # 40 fs average resolution
    'DecayTimeResolutionBias': 0., # if there is a shift
    'DecayTimeResolutionScaleFactor': 1.0, # usually the errors need a bit of scaling

    'AcceptanceFunction': None,

    'constParams': [
        '.*_scalefactor', # anything ending in '_scalefactor'...
        ],
}
