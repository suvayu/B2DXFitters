TARGETS = readTreeDict.cxx libreadTree.so accept

alldicts += readTreeDict.cxx

include Rules.mk

libreadTree.so: readTreeDict.os $(patsubst %.cxx,%.os,$(filter-out accept.cc,$(ccsrc)))
# Mac OS/X hack
ifeq ($(UNAME_SYS),Darwin)
libreadTree.so:	LDLIBS+=-lstdc++ $(ROOTLIBS)
endif

readTreeDict.cxx: readTree.hxx readMCTree.hxx lifetime.hxx readTreeLinkDef.h

accept: libreadTree.so
accept:	LDLIBS+=-lstdc++ $(ROOTLIBS)
