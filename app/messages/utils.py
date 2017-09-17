# -*- encoding: utf8 -*-
import urllib2
import urllib
import json
import gzip

from StringIO import StringIO
from models import *

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
                    list_fragment.append(Segment.serialize(result))

    return list_fragment

def dl_distance(s1, s2, substitutions=[], deletions = [], insertions =[],  symetric=True,
                returnMatrix=False, printMatrix=False, nonMatchingEnds=False, transposition=True,
                secondHalfDiscount=False):
    """
    Return DL distance between s1 and s2. Default cost of substitution, insertion, deletion and transposition is 1
    substitutions is list of tuples of characters (what, substituted by what, cost),
        maximal value of substitution is 2 (ie: cost deletion & insertion that would be otherwise used)
        eg: substitutions=[('a','e',0.4),('i','y',0.3)]
    symetric=True mean that cost of substituting A with B is same as B with A
    returnMatrix=True: the matrix of distances will be returned, if returnMatrix==False, then only distance will be returned
    printMatrix==True: matrix of distances will be printed
    transposition=True (default): cost of transposition is 1. transposition=False: cost of transpositin is Infinity
    """
    if not isinstance(s1, unicode):
        s1 = unicode(s1, "utf8")
    if not isinstance(s2, unicode):
        s2 = unicode(s2, "utf8")

    from collections import defaultdict
    dels = defaultdict(lambda: 1)
    ins = defaultdict(lambda : 1)
    subs = defaultdict(lambda: 1)  # default cost of substitution is 1
    for a, b, v in substitutions:
        subs[(a, b)] = v
        if symetric:
            subs[(b, a)] = v
    for a, v in deletions:
        dels[a] = v
    for a, v in insertions:
        ins[a] = v

    if nonMatchingEnds:
        matrix = [[j for j in range(len(s2) + 1)] for i in range(len(s1) + 1)]
    else:  # start and end are aligned
        matrix = [[i + j for j in range(len(s2) + 1)] for i in range(len(s1) + 1)]
    # matrix |s1|+1 x |s2|+1 big. Only values at border matter
    half1 = len(s1) / 2
    half2 = len(s2) / 2
    for i in range(len(s1)):
        for j in range(len(s2)):
            ch1, ch2 = s1[i], s2[j]
            if ch1 == ch2:
                cost = 0
            else:
                cost = subs[(ch1, ch2)]
            if secondHalfDiscount and (s1 > half1 or s2 > half2):
                deletionCost, insertionCost = 0.6, 0.6
            else:
                deletionCost, insertionCost = 1, 1

            deletionCost = dels[ch1]
            insertionCost = ins[ch2]
            matrix[i + 1][j + 1] = min([matrix[i][j + 1] + deletionCost,  # deletion
                                        matrix[i + 1][j] + insertionCost,  # insertion
                                        matrix[i][j] + cost  # substitution or no change
                                        ])

            if transposition and i >= 1 and j >= 1 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                matrix[i + 1][j + 1] = min([matrix[i + 1][j + 1],
                                            matrix[i - 1][j - 1] + cost])

    if printMatrix:
        print "     ",
        for i in s2:
            print i, "",
        print
        for i, r in enumerate(matrix):
            if i == 0:
                print " ", r
            else:
                print s1[i - 1], r
    if returnMatrix:
        return matrix
    else:
        return matrix[-1][-1]


def dl_ratio(s1, s2, **kw):
    'returns distance between s1&s2 as number between [0..1] where 1 is total match and 0 is no match'
    try:
        return 1 - (dl_distance(s1, s2, **kw)) / (2.0 * max(len(s1), len(s2)))
    except ZeroDivisionError:
        return 0.0


def match_list(s, l, **kw):
    '''
    returns list of elements of l with each element having assigned distance from s
    '''
    return map(lambda x: (dl_distance(s, x, **kw), x), l)


def pick_N(s, l, num=3, **kw):
    ''' picks top N strings from options best matching with s
        - if num is set then returns top num results instead of default three
    '''
    return sorted(match_list(s, l, **kw))[:num]


def pick_one(s, l, **kw):
    try:
        return pick_N(s, l, 1, **kw)[0]
    except IndexError:
        return None


def substring_match(text, s, transposition=True, **kw):  # TODO: isn't backtracking too greedy?
    """
    fuzzy substring searching for text in s
    """
    for k in ("nonMatchingEnds", "returnMatrix"):
        if kw.has_key(k):
            del kw[k]

    matrix = dl_distance(s, text, returnMatrix=True, nonMatchingEnds=True, **kw)

    minimum = float('inf')
    minimumI = 0
    for i, row in enumerate(matrix):
        if row[-1] < minimum:
            minimum = row[-1]
            minimumI = i

    x = len(matrix[0]) - 1
    y = minimumI

    # backtrack:
    while x > 0:
        locmin = min(matrix[y][x - 1],
                     matrix[y - 1][x - 1],
                     matrix[y - 1][x])
        if matrix[y - 1][x - 1] == locmin:
            y, x = y - 1, x - 1
        elif matrix[y - 1][x] == locmin:
            y = y - 1
        elif matrix[y][x - 1] == locmin:
            x = x - 1

    return minimum, (y, minimumI)


def substring_score(s, text, **kw):
    return substring_match(s, text, **kw)[0]


def substring_position(s, text, **kw):
    return substring_match(s, text, **kw)[1]


def substring_search(s, text, **kw):
    score, (start, end) = substring_match(s, text, **kw)
    # print score, (start, end)
    return text[start:end]


def match_substrings(s, l, score=False, **kw):
    'returns list of elements of l with each element having assigned distance from s'
    return map(lambda x: (substring_score(x, s, **kw), x), l)


def pick_N_substrings(s, l, num=3, **kw):
    ''' picks top N substrings from options best matching with s
        - if num is set then returns top num results instead of default three
    '''
    return sorted(match_substrings(s, l, **kw))[:num]


def pick_one_substring(s, l, **kw):
    try:
        return pick_N_substrings(s, l, 1, **kw)[0]
    except IndexError:
        return None
