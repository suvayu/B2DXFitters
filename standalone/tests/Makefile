TARGETS = MyDict.cxx ktest

alldicts += MyDict.cxx

STDOPTFLAGS.GNU = -O0
TUNEFLAGS.GNU   = 

include ../Rules.mk

ktest: ktest.o MyDict.o RooKResModel.o Inverse.o

MyDict.cxx: RooKResModel.h Inverse.h LinkDef.h

ktest: LDLIBS+=-lstdc++ $(ROOTLIBS) -lRooFitCore -lRooFit
