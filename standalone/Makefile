TARGETS = B2DXFittersRflx.cxx libB2DXFitters.so
alldicts += B2DXFittersRflx.cxx

SUBDIRS = readTree

include Rules.mk

# Mac OS/X hack
ifeq ($(UNAME_SYS),Darwin)
B2DXFittersRflx.cxx: CPPFLAGS+=-I. -IB2DXFitters
endif
B2DXFittersRflx.cxx: B2DXFittersDict.h B2DXFittersDict.xml

ifeq ($(UNAME_SYS),Darwin)
# Mac OS/X hack
libB2DXFitters.so: LDLIBS+=-lstdc++ $(ROOTLIBS) -lReflex -lRooFitCore -lRooFit -lRooStats
else
libB2DXFitters.so: LDLIBS+=$(ROOTLIBS) -lReflex -lCintex -lRooFitCore -lRooFit -lRooStats
endif
libB2DXFitters.so: B2DXFittersRflx.os $(patsubst %.cxx,%.os,$(allsrc))
