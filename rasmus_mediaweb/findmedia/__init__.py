from collections import OrderedDict

from .thepiratebay import Finder

_modules = {
    'thepiratebay': Finder
}


class FindManager(object):

    def __init__(self):
        self._searchers = {}
        for k, searcher_class in _modules.items():
            self._searchers[k] = searcher_class()

    def find(self, s, t):
        res = OrderedDict()
        for k, searcher in self._searchers.items():
            res[k] = searcher.perform(s, t)
        return res

find_manager = FindManager()
