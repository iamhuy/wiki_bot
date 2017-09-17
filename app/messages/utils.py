import urllib2
import urllib
import json
import gzip

from StringIO import StringIO


def babelfy(text, annotation_type):
    service_url = 'https://babelfy.io/v1/disambiguate'

    lang = 'EN'
    key  = '61dc9d2b-8bf8-434e-b3ec-08f32e523959'

    params = {
        'text' : text,
        'lang' : lang,
        'key'  : key,
        'annType': annotation_type
    }

    url = service_url + '?' + urllib.urlencode(params)
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)

    list_fragment = []

    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = json.loads(f.read())

        # retrieving data
        for result in data:
                    # retrieving token fragment
                    # new_tuple = {}
                    # charFragment = result.get('charFragment')
                    # new_tuple['start'] = charFragment.get('start')
                    # new_tuple['end'] = charFragment.get('end')
                    # new_tuple['id'] = result.get('babelSynsetID')
                    # new_tuple['score'] = result.get('score')
                    # new_tuple['text'] = text[charFragment.get('start') : charFragment.get('end') + 1]
                    list_fragment.append(result)

    return list_fragment
