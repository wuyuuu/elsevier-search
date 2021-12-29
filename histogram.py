from pyecharts.charts import Bar
from pyecharts import options as opts
import collections
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
import matplotlib.pyplot as plt
import numpy as np

REFRESH = True


def make_query(list_of_keywords, year=None, forbidden=None, ):
    """
    Args:
        list_of_keywords (list[list[str]]): [['adj1','adj2'],['subject1','subject2'],[constraint1, constraint2]]
        year (int or str) : some cover year
    Returns:
        str: "TITLE-ABS-KEY(("adj1" or "adj2") and ("subject1" or "subject2")) AND PUBYEAR IS year)
    """
    ans = ""
    for query_keywords in list_of_keywords:
        s = ""
        for word in query_keywords:
            s += "\"%s\"" % word
            if word != query_keywords[-1]:
                s += ' or '
        ans += '(%s)' % s
        if query_keywords != list_of_keywords[-1]:
            ans += ' and '
    if forbidden:
        ans += 'and not %s' % ''.join(forbidden)
    ans = "TITLE-ABS-KEY(%s)" % ans
    if year is not None:
        if not isinstance(year, str):
            year = str(year)
        ans = ans + ' AND PUBYEAR IS %s' % year
    return ans


def quickSearch(query, verbose=False):
    """
    Args:
        query (str) : query like "TITLE-ABS-KEY(query) AND PUBYEAR IS 2020"
        verbose (bool) : if true, print title of each publications
    Returns:
        int: No. publications for query
    """
    a = ScopusSearch(query, refresh=REFRESH)
    if not REFRESH:
        return a.get_results_size()
    e_ids = a.get_eids()

    # print(a.get_results_size())
    if not verbose:
        return a.get_results_size()
    # dates = []
    for eid in e_ids:
        ab = AbstractRetrieval(eid)
        print(type(ab.title), ab.title)
        print(type(ab.coverDate), ab.coverDate)
        # dates.append(int(ab.coverDate[:4]))
    return a.get_results_size()


def fit_y_poly(x, y, x_curve):
    k = np.polyfit(x, y, 4)
    p = np.poly1d(k)
    pred_y = p(x_curve)
    return pred_y


def draw_hist(list_of_keywords, years_range=range(2011, 2022), verbose=False, forbidden=None):
    """
    Generate scopusSearch query given keywords and cover years
    and visualize histogram of No. publication for 'query' in years_range.
    Save the result in 'imgs/query.pdf'
    Args:
        list_of_keywords (list[list[str]]): [[adj1,adj2],[subject1,subject2]]
        years_range (list[int]): range of cover years
        verbose (bool): if true, show title of each paper

    Returns:
        None
    """
    pubs_per_year = []
    for year in years_range:
        query = make_query(list_of_keywords, year, forbidden=forbidden)
        print('query:%s' % query)
        # import math
        # number_of_publications = 2**(year-2000)
        number_of_publications = quickSearch(query, verbose)
        pubs_per_year.append(int(number_of_publications))
        print(pubs_per_year[-1])
    print(pubs_per_year)
    fontsize = 18
    plt.rcParams['font.size'] = fontsize
    plt.bar(years_range, pubs_per_year)
    x_curve = np.linspace(np.min(years_range[:-1]), np.max(years_range[:-1]), 500)
    pred_y = fit_y_poly(years_range[:-1], pubs_per_year[:-1], x_curve)
    plt.plot(x_curve, pred_y, linestyle='--', c='r', linewidth=4)
    # plt.xticks(years_range)
    plt.xlabel('Year', fontsize=fontsize)
    plt.ylabel('No. publication', fontsize=fontsize)
    plt.tight_layout()
    plt.savefig('imgs/%s' % make_query(list_of_keywords).replace('\"', '') + '.pdf', bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    # visualize trends of multi-person pose estimation
    adj = ["multi-person", "crowd"]
    subject = ["multi-person pose estimation", "human pose estimation"]
    res = ["deep learning", "neural networks", "neural network"]
    draw_hist([adj, subject])

    # visualize trends of efficient human pose estimation
    adj = ["efficient", "real-time"]
    subject = ["human pose estimation"]
    res = ["deep learning", "neural networks", "neural network"]
    draw_hist([adj, subject, res])

    # visualize trends of 3D huamn pose estimation
    adj = ['3D']
    subject = ['human pose estimation']
    draw_hist([adj, subject])

    # visualize trends of multi-modal human pose estimation
    adj = ["multi-modal", "multimodal", "IMUs", "radio signal", "RGB-D"]
    adj2 = ["3D"]
    subject = ["human pose estimation"]
    forbidden = ["distribution"]
    draw_hist([adj, subject], verbose=False, forbidden=forbidden)
