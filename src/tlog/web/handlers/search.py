import base
import math
from tlog.config import Config
from tlog.constants import SEARCH_RESULTS_PER_PAGE
from tornado.web import authenticated
from pyelasticsearch import ElasticSearch

class Handler(base.Handler):

    es = ElasticSearch(Config.data['elasticsearch']['url'])

    @authenticated
    def get(self):
        results = []
        query = self.get_argument('q', None)
        page = int(self.get_argument('p', 0))
        pages = []
        if query:
            results = self.es.search(
                {
                    'filter': {
                        'query': {
                            'query_string': {
                                'query': query,
                                'default_field': 'data.message',
                                'default_operator': 'OR'
                            }
                        },
                    },
                    "sort" : [
                        { "received" : {"order" : "desc"} },
                    ]
                },
                index='logs',
                size=SEARCH_RESULTS_PER_PAGE,
                es_from=SEARCH_RESULTS_PER_PAGE*page,
            )
            pages = self.get_pages(results['hits']['total'])
        self.render(
            'search.html',
            title='Search',
            results=results,
            pages=pages,
            current_page=page,
        )

    def get_pages(self, total_results):
            pages = []
            if total_results > 0:
                for p in xrange(int(math.ceil(total_results / SEARCH_RESULTS_PER_PAGE))):
                    pages.append(p)
            return pages