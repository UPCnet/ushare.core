# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import ushare.core


class UshareCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=ushare.core)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ushare.core:default')


USHARE_CORE_FIXTURE = UshareCoreLayer()


USHARE_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(USHARE_CORE_FIXTURE,),
    name='UshareCoreLayer:IntegrationTesting'
)


USHARE_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(USHARE_CORE_FIXTURE,),
    name='UshareCoreLayer:FunctionalTesting'
)


USHARE_CORE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        USHARE_CORE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='UshareCoreLayer:AcceptanceTesting'
)
