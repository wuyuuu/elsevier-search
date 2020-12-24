from pyecharts.charts import Bar
from pyecharts import options as opts
import collections
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
import matplotlib.pyplot as plt


def make_query(list_of_keywords, year=None, forbidden=None):
    """
    Args:
        forbidden (List[str]) : forbidden keywords
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
    if forbidden is not None:
        for forbidden_word in forbidden:
            ans += " and not %s" % forbidden_word

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
    a = ScopusSearch(query, refresh=True)
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


def draw_hist(list_of_keywords, years_range=range(2010, 2021), verbose=False, forbidden=None):
    """
    Generate scopusSearch query given keywords and cover years
    and visualize histogram of No. publication for 'query' in years_range.
    Save the result in 'imgs/query.pdf'
    Args:
        forbidden (list[str]): forbidden keywords
        list_of_keywords (list[list[str]]): [[adj1,adj2],[subject1,subject2]]
        years_range (list[int]): range of cover years
        verbose (bool): if true, show title of each paper

    Returns:
        None
    """
    pubs_per_year = []
    for year in years_range:
        query = make_query(list_of_keywords, year, forbidden)
        print('query:%s' % query)
        number_of_publications = quickSearch(query, verbose)
        pubs_per_year.append(number_of_publications)
    plt.bar(years_range, pubs_per_year)
    plt.xlabel('Year')
    plt.ylabel('No. publication')
    path = make_query(list_of_keywords,None,forbidden)
    path.replace(' ','_')
    path.strip('"')
    plt.savefig(
        'imgs/%s' % path + '.pdf')
    plt.close()


if __name__ == '__main__':
    # visualize trends of multi-person pose estimation
    adj = ["multi-person", "crowd"]
    subject = ["multi-person pose estimation", "human pose estimation"]
    draw_hist([adj, subject])

    # visualize trends of efficient human pose estimation
    adj = ["efficient", "real-time"]
    subject = ["human pose estimation"]
    draw_hist([adj, subject])

    # visualize trends of 3D huamn pose estimation
    adj = ['3D']
    subject = ['human pose estimation']
    draw_hist([adj, subject])

    # visualize trends of multi-modal human pose estimation
    adj = ["multi-modal", "multimodal", "IMUs", "radio signal"]
    subject = ["human pose estimation"]
    forbidden = ["distribution"]
    draw_hist([adj, subject], verbose=True, forbidden=forbidden)
