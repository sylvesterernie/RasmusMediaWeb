import requests
from bs4 import BeautifulSoup


def _extract_info(soup):
    info = {}
    v = soup.select('.detName a')
    if len(v) == 0:
        return
    else:
        v = v[0]
    info['name'] = v.string
    info['url'] = v.attrs['href']

    for v in soup.select('a'):
        href = v.attrs['href']
        if href.startswith('magnet:'):
            info['magnet_uri'] = href
            break
    return info


class Finder(object):

    url_pattern = 'http://thepiratebay.se/search/%s/0/7/%s'

    # these map tpb category id's to our media type's
    type_map = {
        'movies': '207',
        'tvshows': '208',
        'music': '101',
    }

    def perform(self, s, t):
        r = requests.get(self.url_pattern % (s, self.type_map[t]))
        soup = BeautifulSoup(r.text)
        res = []
        for entry in soup.select('#searchResult tr'):
            parsed = _extract_info(entry)
            if parsed is not None:
                res.append(parsed)
        return res
