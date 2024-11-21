# -*- coding: utf-8 -*-
from OFS.Image import Image
from Products.PlonePAS.interfaces.membership import IMembershipTool
from Products.PlonePAS.utils import scale_image

from plone import api
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements


class IPortraitUploadAdapter(Interface):
    """ The marker interface for the portrait upload adapter used for implement
        special actions after upload. The idea is to have a default (core)
        action and then other that override the default one using IBrowserLayer.
    """


class PortraitUploadAdapter(object):
    """ Default adapter for portrait custom actions """
    implements(IPortraitUploadAdapter)
    adapts(IMembershipTool, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, portrait, safe_id):
        if portrait and portrait.filename:
            scaled, mimetype = scale_image(portrait)
            portrait = Image(id=safe_id, file=scaled, title='')
            membertool = api.portal.get_tool(name='portal_memberdata')
            membertool._setPortrait(portrait, safe_id)
