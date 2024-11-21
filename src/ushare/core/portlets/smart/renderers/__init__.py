# -*- coding: utf-8 -*-
from plone import api


class PortletItemRenderer(object):

    def __init__(self, context):
        self.item = context

    def __call__(self, portletrenderer, **kwargs):
        self.portlet = portletrenderer
        self.request = portletrenderer.request
        self.context = portletrenderer.context

        for key, value in kwargs.items():
            setattr(self, key, value)

        return {'css_class': self.css_class,
                'html': self.template(self)}


class PortletContainerRenderer(object):

    def __init__(self, context):
        self.portlet = context
        self.context = self.portlet.context
        self.request = self.portlet.request

    def __call__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        return self.template(self)

    def isAnon(self):
        if not api.user.is_anonymous():
            return False
        return True
