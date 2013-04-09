TARGETS = B2DXFittersRflx.cxx libB2DXFitters.so
alldicts += B2DXFittersRflx.cxx

SUBDIRS = readTree

include Rules.mk

# Mac OS/X hack
B2DXFittersRflx.cxx: CPPFLAGS+=-I. -IB2DXFitters
B2DXFittersRflx.cxx: B2DXFittersDict.h B2DXFittersDict.xml

# Mac OS/X hack
libB2DXFitters.so: LDLIBS+=-lstdc++ $(ROOTLIBS) -lReflex -lRooFitCore -lRooFit -lRooStats
libB2DXFitters.so: B2DXFittersRflx.os $(patsubst %.cxx,%.os,$(allsrc))
