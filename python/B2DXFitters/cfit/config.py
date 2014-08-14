# coding=utf-8
"""cFit configuration classes

   @author Suvayu Ali
   @email  Suvayu dot Ali at cern dot ch
   @date   2014-08-14

"""


from logging import getLogger, error, warning, debug
logger = getLogger(__name__)

import os
from math import pi, log
from .utils import updateConfigDict


class ConfigReader(object):
    """Configuration reader for the cfit.

    This class reads files or strings and converts them to a
    dictionary which can be used to configure the cfit.

    Initialisation:
    baseconf -- dictionary used as base configuration
    pers     -- personality file with additional configurations (dict)
    fit      -- list of configuration files for fitting only
    gen      -- list of configuration files for generation only
    fitstr   -- list of configuration strings for fitting only
    genstr   -- list of configuration strings for generation only

    """

    def __init__(self, baseconf, pers, fit=[], gen=[], fitstr=[], genstr=[]):
        if pers:
            persname = pers.split('/')[-1] # strip leading path
            persname = persname.split('.')[0] # strip extension
            self._baseconf = updateConfigDict(baseconf,
                                              {'Personality': persname})
            self._baseconf = self.parse_file(pers, self._baseconf)
        from copy import deepcopy
        self._fitconf = deepcopy(self._baseconf)
        self._genconf = deepcopy(self._baseconf)
        def for_each(itr, retval, fn): # recursive for each
            for item in itr:
                if not item: continue
                retval = fn(item, retval)
            return retval
        self._fitconf = for_each(fit, self._fitconf, self.parse_file)
        self._fitconf = for_each(fit, self._fitconf, self.parse_str)
        self._genconf = for_each(gen, self._genconf, self.parse_file)
        self._genconf = for_each(gen, self._genconf, self.parse_str)

    @classmethod
    def parse(cls, src, srcname = '<string>'):
        """Parse string return result

        src     -- string to parse (python source)
        srcname -- source filename (default '<string>')

        """
        try:
            d = eval(compile(src, srcname, 'eval'))
        except:
            error('Invalid config dictionary')
            raise
        return d

    @classmethod
    def parse_str(cls, string, conf):
        """Parse string and update config.

        string -- the string to parse
        conf   -- config to update

        """
        return updateConfigDict(conf, cls.parse(string))

    @classmethod
    def parse_file(cls, fname, conf):
        """Parse file and update config.

        fname -- filename of file to parse
        conf  -- config to update

        """
        try:
            lines = file(fname, 'r').readlines()
        except:
            error('Could not read config dictionary.')
            raise
        return updateConfigDict(conf, cls.parse(''.join(lines), fname))

    def base_config(self):
        """Base configuration"""
        return self._baseconf

    def fit_config(self):
        """Fit configuration"""
        return self._fitconf

    def gen_config(self):
        """Generation configuration"""
        return self._genconf
