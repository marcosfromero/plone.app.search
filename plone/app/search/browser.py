from Products.Five.browser import BrowserView
from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone')


class Search(BrowserView):

    sections_cache = {}

    def results(self, query=None, batch=False, b_size=30, b_start=0, **kw):
        """ Get properly wrapped search results from the catalog.
        Everything in Plone that performs searches should go through this view.
        'query' (optional) should be a dictionary of catalog parameters.
        You can also pass catalog parameters as individual named keywords.
        """
        if query is not None:
            kw.update(query)
        kw.update(getattr(self.request, 'form', {}))
        if not kw:
            return IContentListing([])

        kw = self.ensureFriendlyTypes(kw)

        # In order to wrap the catalog results with some checkups like prevent
        # site error when searching for '*' we don't call catalog directly, but
        # queryCatalog instead
        results = IContentListing(self.context.queryCatalog(kw))
        if batch:
            from Products.CMFPlone import Batch
            batch = Batch(results, b_size, int(b_start), orphan=0)
            return IContentListing(batch)
        return results

    def getSortOptions(self):
        """ Sorting options for search results view. """

        return(
            sortOption(self.request, _(u'relevance'), ''),
            sortOption(self.request, _(u'date (newest first)'),
                                     'Date',
                                     reverse=True),
            sortOption(self.request, _(u'alphabetically'), 'sortable_title'),
        )

    def showAdvancedSearch(self):
        """Whether we need to show advanced search options a.k.a. filters?"""
        if not self.request.get('advanced_search', None):
            return False
        elif self.request.get('advanced_search', None) == 'False':
            return False
        elif self.request.get('advanced_search', None) == 'True':
            return True

    def advancedSearchTrigger(self):
        """URL builder for show/close advanced search filters."""
        query = self.request.get('QUERY_STRING', None)
        if not query:
            return self.request.get('ACTUAL_URL', self.context.absolute_url())
        if 'advanced_search' in query:
            if 'advanced_search=True' in query:
                query = query.replace('advanced_search=True', '')
            if 'advanced_search=False' in query:
                query = query.replace('advanced_search=False', '')
        else:
            query = query + '&advanced_search=True'

        return self.request.get('ACTUAL_URL',
                                self.context.absolute_url()) + '?' + query

    def section(self, url):
        """ Returns a section in which the object at the passed url is
        contained. Section is a first-level folder in Plone root.

        For objects that are contained in Plone root object, we just return
        None as we don't want to display anything on the template.

        It does that by first removing the portal url part from the object's
        url, including the Plone instance id in non-virtual-hostname
        environments.

        Then it splits the path with '/', taking the second item which is
        the section's id.

        Lastly an object is retrieved from the Plone root object that has
        the id of the section we are looking for.

        Simple caching is put in place to prevent waking up section object for
        objects under the same section.
        """
        # plone root object
        url_tool = getToolByName(self.context, "portal_url")
        portal = url_tool.getPortalObject()

        # truncate away http, domain and plone instance id
        path = url.split(url_tool.getPortalPath())[1]

        # don't show location for first-level objects
        # -> ['', 'front-page']
        if len(path.split('/')) < 3:
            return None

        # get sections's id
        section_id = path.split('/')[1]

        # is this section's Title already stored in sections_cache cache
        # dictionary?
        if section_id in self.sections_cache.keys():
            return self.sections_cache[section_id]

        # get section object
        section = portal[section_id]

        # store title and id in cache
        self.sections_cache[section_id] = section.title

        return section.title


class sortOption(object):

    def __init__(self, request, title, sortkey='', reverse=False):
        self.request = request
        self.title = title
        self.sortkey = sortkey
        self.reverse = reverse

    def selected(self):
        sort_on = self.request.get('sort_on') and \
                  self.request.get('sort_on') or \
                  ''
        return sort_on == self.sortkey

    def url(self):
        q = {}
        q.update(self.request.form)
        if 'sort_on' in q.keys():
            del q['sort_on']
        if 'sort_order' in q.keys():
            del q['sort_order']
        q['sort_on'] = self.sortkey
        if self.reverse:
            q['sort_order'] = 'reverse'

        base_url = self.request.URL
        # After the AJAX call the request is changed and thus the URL part of
        # it as well. In this case we need to tweak the URL to point to have
        # correct URLs
        if '@@updated_search' in base_url:
            base_url = base_url.replace('@@updated_search', '@@search')
        return base_url + '?' + make_query(q)
