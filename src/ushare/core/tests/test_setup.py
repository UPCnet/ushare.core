# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from ushare.core.testing import USHARE_CORE_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that ushare.core is properly installed."""

    layer = USHARE_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ushare.core is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'ushare.core'))

    def test_browserlayer(self):
        """Test that IUshareCoreLayer is registered."""
        from ushare.core.interfaces import (
            IUshareCoreLayer)
        from plone.browserlayer import utils
        self.assertIn(IUshareCoreLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = USHARE_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ushare.core'])

    def test_product_uninstalled(self):
        """Test if ushare.core is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'ushare.core'))

    def test_browserlayer_removed(self):
        """Test that IUshareCoreLayer is removed."""
        from ushare.core.interfaces import \
            IUshareCoreLayer
        from plone.browserlayer import utils
        self.assertNotIn(IUshareCoreLayer, utils.registered_layers())
