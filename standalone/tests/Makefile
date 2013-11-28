TARGETS = MyDict.cxx ktest

alldicts += MyDict.cxx

STDOPTFLAGS.GNU = -O0
TUNEFLAGS.GNU   = 

include ../Rules.mk

ktest: ktest.o MyDict.o RooKResModel.o RooKConvGenContext.o Inverse.o

MyDict.cxx: B2DXFitters/RooKResModel.h B2DXFitters/Inverse.h B2DXFitters/RooKConvGenContext.h LinkDef.h

ktest: LDLIBS+=-lstdc++ $(ROOTLIBS) -lRooFitCore -lRooFit
