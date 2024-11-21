import unittest2 as unittest
from ushare.core.testing import USHARE_CORE_INTEGRATION_TESTING
from AccessControl import Unauthorized
from zope.component import getMultiAdapter, queryUtility
from zope.interface import alsoProvides
from Products.CMFCore.utils import getToolByName

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from plone.app.testing import applyProfile
import urllib2

import transaction


class IntegrationTest(unittest.TestCase):

    layer = USHARE_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def testPortalConstrains(self):
        portal_allowed_types = ['Folder', 'File', 'Image', 'Document','Collection', 'Event', 'Link', 'News Item']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.assertEqual(sorted([ct.id for ct in self.portal.allowedContentTypes()]), sorted(portal_allowed_types))

    def testLinkBehavior(self):
        """Test for Link behavior and related index and metadata"""
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'f2', title=u"Soc una carpeta")
        f2 = portal['f2']
        f2.invokeFactory('Link', 'enllac', title=u"Soc un link")
        link = f2['enllac']
        link.open_link_in_new_window = False
        link.reindexObject()

        self.assertEqual(link.open_link_in_new_window, False)

        results = portal.portal_catalog.searchResults(portal_type='Link')
        self.assertEqual(results[0].open_link_in_new_window, False)

        link.open_link_in_new_window = True
        link.reindexObject()

        results = portal.portal_catalog.searchResults(portal_type='Link')
        self.assertEqual(results[0].open_link_in_new_window, True)

    def testAdapters(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Document', 'test_adapter', title=u"Soc una pagina")
        from ushare.core.adapters import IImportant
        obj = IImportant(self.portal.test_adapter)
        self.assertEqual(obj.is_important, False)
        obj.is_important = True
        obj2 = IImportant(self.portal.test_adapter)
        self.assertEqual(obj2.is_important, True)

    def test_favorites(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'prova', title=u"Soc una carpeta")
        prova = self.portal['prova']
        prova.invokeFactory('Folder', 'prova', title=u"Soc una carpeta")
        prova2 = prova['prova']

        from ushare.core.adapters.favorites import IFavorite
        IFavorite(prova2).add(TEST_USER_NAME)
        self.assertTrue(TEST_USER_NAME in IFavorite(prova2).get())
        self.assertTrue(TEST_USER_NAME not in IFavorite(prova).get())

    def test_protected_content(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory('Folder', 'test_folder', title=u"Soc una carpeta")
        self.portal.test_folder.invokeFactory('Document', 'test_document', title=u"Soc un document")
        from ushare.core.interfaces import IProtectedContent
        alsoProvides(self.portal.test_folder, IProtectedContent)
        setRoles(self.portal, TEST_USER_ID, ['Reader', 'Editor'])

        self.portal.test_folder.manage_delObjects('test_document')

        self.assertRaises(Unauthorized, self.portal.manage_delObjects, 'test_folder')
