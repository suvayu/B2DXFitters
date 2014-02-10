# Author: Pieter David

################################################################################
## Configuration                                                              ##
################################################################################
from Configurables import LHCbApp, LoKiSvc
LHCbApp(DataType="2012", Simulation=True) # TODO: add appropriate database tags if extrapolating tracks

from LHCbKernel.Configuration import VERBOSE
from Configurables import OfflineVertexFitter

#OfflineVertexFitter().OutputLevel = VERBOSE


from Bender.Utils import *

## in case you want to run over data:
# replace LHCbApp at the top by DaVinci (and for microDST, pass InputType="MDST" and set RootInTES)
# setData( files ) # cleanest option: pass LFNs and grid=True (needs a grid proxy) or generate a catalog by hand
## use run(1), ls() and get("Phys/YOURSTRIPPINGSTREAM/STRIPPINGLINE/Particles") to have a look at the particles
## or run dst-explorer (which will detect all this automatically)

################################################################################
## Apply configuration and initialize                                         ##
################################################################################
gaudi = appMgr()
gaudi.initialize()

## containers to keep a reference to objects alive
objectKeeper = set()
import atexit
atexit.register(objectKeeper.clear) # register *before* Bender's exit handler that will finalize the application manager

################################################################################
## "Interactive" part                                                         ##
################################################################################

from Bender.Main import *
import math
import numpy as np

## tools and services
particle2StateTool = gaudi.toolSvc().create("Particle2State", interface=cpp.IParticle2State)
particleCombiner   = gaudi.toolSvc().create("OfflineVertexFitter", interface=cpp.IParticleCombiner)
partPropSvc        = gaudi.service("LHCb::ParticlePropertySvc", interface=LHCb.IParticlePropertySvc)

def makeParticleFromPositionAndThreeMomentum( position, threeMomentum, pid="pi+", trackCovariance=None):
    """
    Create a charged particle with an unffited track with one state

    A default track covariance matrix is generated, if not given
    """
    partProp = partPropSvc.find(pid)
    st = LHCb.State()
    objectKeeper.add(st)
    st.setState( position.X(),position.Y(),position.Z(), threeMomentum.X()/threeMomentum.Z(), threeMomentum.Y()/threeMomentum.Z(), partProp.charge()/threeMomentum.Mag() )
    if trackCovariance is None: # default track covariance matrix
        trackCovariance = Gaudi.TrackSymMatrix()
        # TODO make a more realistic estimate
        trackCovariance[0,0] = 0.015**2 # x^2
        trackCovariance[1,1] = 0.015**2 # y^2
        trackCovariance[2,2] = 0.001**2 # tx^2
        trackCovariance[3,3] = 0.002**2 # ty^2
        trackCovariance[4,4] = 1./(.004*threeMomentum.Mag())**2# (q/p)^2
    st.setCovariance(trackCovariance)
    track = LHCb.Track()
    objectKeeper.add(track)
    track.addToStates(st)
    proto = LHCb.ProtoParticle()
    objectKeeper.add(proto)
    proto.setTrack(track)
    part = LHCb.Particle()
    objectKeeper.add(part)
    part.setProto(proto)
    part.setParticleID(partProp.particleID())
    part.setMeasuredMass(partProp.mass())
    particle2StateTool.state2Particle(st, part)
    return part

def combineParticles( daughters, motherPid="D_s+", combiner=particleCombiner ):
    """
    Create a new LHCb::Particle with motherPid from daughters, using IParticleCombiner tool combiner
    """
    mother = LHCb.Particle()
    objectKeeper.add(mother)
    partProp = partPropSvc.find(motherPid)
    mother.setParticleID(partProp.particleID())
    motherVertex = LHCb.Vertex()
    objectKeeper.add(motherVertex)

    daughtersVec = LHCb.Particle.ConstVector()
    for d in daughters:
        daughtersVec.push_back(d)

    combiner.combine( daughtersVec, mother, motherVertex )

    return mother

# str(TLorentzVector v) -> "( v.x0, v.x1, v.x2, v.x3 )"
def lorentzToString(ltz):
    return "( {0}, {1}, {2}, {3} )".format(ltz.T(), ltz.X(), ltz.Y(), ltz.Z())
ROOT.TLorentzVector.__str__ = lorentzToString
del lorentzToString


## Generate a decay
pdgMasses = dict( (name, partPropSvc.find(name).mass()) for name in ("B_s0", "D_s+", "K+", "pi+") )

genBs = ROOT.TLorentzVector()
genBs.SetXYZM(2500.*MeV, 2500.*MeV, 30000.*MeV, pdgMasses["B_s0"]+5.*MeV)

genBsDaugMasses = np.array([ pdgMasses["D_s+"]+5.*MeV, pdgMasses["K+"]+2.*MeV ])
genBsDecay = ROOT.TGenPhaseSpace()
if not genBsDecay.SetDecay(genBs, 2, genBsDaugMasses):
    print "Problem with Bs decay"
genBsDecay.Generate()
genDs   = genBsDecay.GetDecay(0)
genBach = genBsDecay.GetDecay(1)
print "Bs decay {0:s} -> Ds {1:s} + K {2:s}".format(genBs, genDs, genBach)

genDsDaugMasses = np.array([ pdgMasses["K+"]-5.*MeV, pdgMasses["K+"]-2.*MeV, pdgMasses["pi+"]+2.*MeV ])
genDsDecay = ROOT.TGenPhaseSpace()
if not genDsDecay.SetDecay(genDs, 3, genDsDaugMasses):
    print "Problem with Ds decay"
genDsDecay.Generate()
genDsd1 = genDsDecay.GetDecay(0)
genDsd2 = genDsDecay.GetDecay(1)
genDsd3 = genDsDecay.GetDecay(2)
print "Ds decay {0:s} -> K {1:s} + K {2:s} + pi {3:s}".format(genDs, genDsd1, genDsd2, genDsd3)

trueBsVertex = ROOT.TVector3(0., 0., 0.)
genDsFlight = genDs.BoostVector().Unit(); genDsFlight.SetMag(10.*mm)
trueDsVertex = trueBsVertex + genDsFlight


## make reco-like particles from (smeared) truth
bachelor = makeParticleFromPositionAndThreeMomentum(trueBsVertex+ROOT.TVector3( .010,-.030,.000), genBach.Vect(), pid="K+" )
Ddaug1   = makeParticleFromPositionAndThreeMomentum(trueDsVertex+ROOT.TVector3( .020, .020,.000), genDsd1.Vect(), pid="K+"  )
Ddaug2   = makeParticleFromPositionAndThreeMomentum(trueDsVertex+ROOT.TVector3(-.020,-.050,.000), genDsd2.Vect(), pid="K-"  )
Ddaug3   = makeParticleFromPositionAndThreeMomentum(trueDsVertex+ROOT.TVector3(-.030,-.020,.000), genDsd3.Vect(), pid="pi-" )

print "Combining D daughters", Ddaug1, Ddaug2, Ddaug3
Ds = combineParticles( (Ddaug1, Ddaug2, Ddaug3), motherPid="D_s-" )
print "into", Ds
print "Combining with", bachelor
Bs = combineParticles( (Ds, bachelor), motherPid="B_s0" )
print "into", Bs
