TARGETS = tagcomb tagcomb-covstudy eps

include Rules.mk

eps: CXX:=$(CC)

$(TARGETS): CC=$(CXX)
$(TARGETS): LDLIBS+=$(ROOTLIBS)
