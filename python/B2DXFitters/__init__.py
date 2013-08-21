# @file python/B2DXFitters/__init__.py
#
# @author Manuel Schiller <manuel.schiller@nikhef.nl>
# @date 2013-08-14
#
# common initialisation for python modules, loading libs etc.
#
# if you plan to use these B2DXFitter classes in your code, put a
#
# @begincode
# import B2DXFitters, ROOT
# from ROOT import RooFit
# @endcode
#
# at the beginning of your script

__initialised = False

if not __initialised:
    __initialised = True
    import os, ROOT
    # avoid memory leaks - will have to explicitly relinquish and acquire
    # ownership if required, but PyROOT does not do what it thinks best without
    # our knowing what it does
    ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
    # enable ROOT to understand Reflex dictionaries
    ROOT.gSystem.Load('libCintex')
    ROOT.Cintex.Enable()
    # load RooFit
    ROOT.gSystem.Load('libRooFit')
    # load our own B2DXFitters library
    if 'URANIASYSROOT' in os.environ.keys():
        ROOT.gSystem.Load('%s/%s/libB2DXFittersDict' % (
            os.environ['B2DXFITTERSROOT'], os.environ['CMTCONFIG']))
        ROOT.gSystem.Load('%s/%s/libB2DXFittersLib' % (
            os.environ['B2DXFITTERSROOT'], os.environ['CMTCONFIG']))
    else:
        # running in standalone mode, we have to load things ourselves
        ROOT.gSystem.Load('%s/standalone/libB2DXFitters' %
                os.environ['B2DXFITTERSROOT'])
    
    # small helper to figure out if we're running from inside gdb
    def in_gdb():
        import os
        proclist = dict(
            (l[0], l[1:]) for l in (
                lraw.replace('\n', '').replace('\r','').split()
                for lraw in os.popen('ps -o pid= -o ppid= -o comm=').readlines()
                )
            )
        pid = os.getpid()
        while pid in proclist:
            if 'gdb' in proclist[pid][1]: return True
            pid = proclist[pid][0]
        return False
    
    if in_gdb():
        # when running in a debugger, we want to make sure that we do not
        # handle any signals, so the debugger can catch SIGSEGV and friends,
        # and we can poke around
        ROOT.SetSignalPolicy(ROOT.kSignalFast)
        ROOT.gEnv.SetValue('Root.Stacktrace', '0')
