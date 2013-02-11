TARGETS = B2DXFittersRflx.cxx libB2DXFitters.so
alldicts += B2DXFittersRflx.cxx

SUBDIRS = readTree

include Rules.mk

B2DXFittersRflx.cxx: B2DXFittersDict.h B2DXFittersDict.xml

libB2DXFitters.so: B2DXFittersRflx.os $(patsubst %.cxx,%.os,$(allsrc))
