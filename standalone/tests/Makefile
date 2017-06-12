TARGETS = MyDict.cxx ktest

alldicts += MyDict.cxx

# C++14
CXXSTD.GNU = -std=c++14
CXXSTD.Clang = -std=c++14
CXXSTD.Intel = -std=c++14

STDOPTFLAGS.GNU = -O0
TUNEFLAGS.GNU   = 

include ../Rules.mk

ifeq ($(ROOTCONFIG_ROOT56),ROOT6)
    REFLEXLIBS=
else
    REFLEXLIBS=-lReflex -lCintex
endif

ktest: ktest.o MyDict.o RooKResModel.o RooKConvGenContext.o Inverse.o

MyDict.cxx: B2DXFitters/RooKResModel.h B2DXFitters/Inverse.h B2DXFitters/RooKConvGenContext.h LinkDef.h

ktest: LDLIBS+=-lstdc++ $(ROOTLIBS) -lRooFitCore -lRooFit
