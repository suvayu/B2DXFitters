TARGETS = B2DXFittersRflx.cxx libB2DXFitters.so
alldicts += B2DXFittersRflx.cxx

SUBDIRS = readTree taggingtoy

STDOPTFLAGS.GNU = -O0
TUNEFLAGS.GNU   = 

# C++14
CXXSTD.GNU = -std=c++14
CXXSTD.Clang = -std=c++14
CXXSTD.Intel = -std=c++14

include Rules.mk
-include local.mk

# Mac OS/X hack
ifeq ($(UNAME_SYS),Darwin)
B2DXFittersRflx.cxx: CPPFLAGS+=-I. -IB2DXFitters
endif
B2DXFittersRflx.cxx: B2DXFittersDict.h B2DXFittersDict.xml

ifeq ($(ROOTCONFIG_ROOT56),ROOT6)
    REFLEXLIBS=
else
    REFLEXLIBS=-lReflex -lCintex
endif

ifeq ($(UNAME_SYS),Darwin)
# Mac OS/X hack
libB2DXFitters.so: LDLIBS+=-lstdc++ $(ROOTLIBS) $(REFLEXLIBS) -lRooFitCore -lRooFit -lRooStats
else
libB2DXFitters.so: LDLIBS+=$(ROOTLIBS) $(REFLEXLIBS) -lRooFitCore -lRooFit -lRooStats
endif
libB2DXFitters.so: B2DXFittersRflx.os $(patsubst %.cxx,%.os,$(allsrc))
