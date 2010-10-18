import unittest2 as unittest

from zope.configuration import xmlconfig

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

class SearchLayer(PloneSandboxLayer):
    """Install plone.app.search"""
    
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.app.contentlisting
        import plone.app.search        
        xmlconfig.file('configure.zcml',
                       plone.app.contentlisting, context=configurationContext)
        xmlconfig.file('configure.zcml',
                       plone.app.search, context=configurationContext)

class SearchPerformance100Layer(SearchLayer):
    
    def setUpPloneSite(self, portal):
        print "Testing performance with 100 pages"

        setRoles(portal, TEST_USER_NAME, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'test-folder')
        f = portal['test-folder']
        for i in range(0,100):
            f.invokeFactory('Document', 'my-page'+str(i), text='spam spam ham eggs')
        setRoles(portal, TEST_USER_NAME, ['Member'])

        # Commit so that the test browser sees these objects
        import transaction
        transaction.commit()
        
    def tearDownPloneSite(self, portal):
        setRoles(portal, TEST_USER_NAME, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.manage_delObjects('test-folder')
        setRoles(portal, TEST_USER_NAME, ['Member'])
        
class SearchPerformance1000Layer(SearchLayer):
    
    def setUpPloneSite(self, portal):
        print "Testing performance with 1000 pages"
            
        setRoles(portal, TEST_USER_NAME, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'test-folder')
        f = portal['test-folder']        
        for i in range(0,1000):
            f.invokeFactory('Document', 'my-page'+str(i), text='spam spam ham eggs')
        setRoles(portal, TEST_USER_NAME, ['Member'])    
    
        # Commit so that the test browser sees these objects
        import transaction
        transaction.commit() 
        
    def tearDownPloneSite(self, portal):
        setRoles(portal, TEST_USER_NAME, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.manage_delObjects('test-folder')
        setRoles(portal, TEST_USER_NAME, ['Member'])        
             

SEARCH_FIXTURE = SearchLayer()
SEARCH_PERFORMANCE100_FIXTURE = SearchPerformance100Layer()
SEARCH_PERFORMANCE1000_FIXTURE = SearchPerformance1000Layer()

SEARCH_INTEGRATION_TESTING = IntegrationTesting(bases=(SEARCH_FIXTURE,), 
                                                name="Search:Integration")
SEARCH_FUNCTIONAL_TESTING = FunctionalTesting(bases=(SEARCH_FIXTURE,), 
                                              name="Search:Functional")
SEARCH_PERFORMANCE100_FUNCTIONAL_TESTING = FunctionalTesting(bases=(SEARCH_PERFORMANCE100_FIXTURE,), name="Search Performance 100:Functional")
SEARCH_PERFORMANCE1000_FUNCTIONAL_TESTING = FunctionalTesting(bases=(SEARCH_PERFORMANCE1000_FIXTURE,), name="Search Performance 1000:Functional")

class SearchTestCase(unittest.TestCase):
    """We use this base class for all tahe tests in this package. If necessary,
    we can put common utility or setup code in here. This applies to unit 
    test cases.
    """
    layer = SEARCH_INTEGRATION_TESTING

class SearchFunctionalTestCase(SearchTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.
    """
    layer = SEARCH_FUNCTIONAL_TESTING
    
class Search100FunctionalTestCase(SearchTestCase):
    """Test layer for performance testing with 100 objects
    """
    layer = SEARCH_PERFORMANCE100_FUNCTIONAL_TESTING    
    
class Search1000FunctionalTestCase(SearchTestCase):
    """Test layer for performance testing with 1000 objects
    """
    layer = SEARCH_PERFORMANCE1000_FUNCTIONAL_TESTING     