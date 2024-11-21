# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IContentish
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.contenttypes.interfaces import IImage
from plone.app.portlets.portlets.base import IPortletRenderer
from zope.component import adapts
from zope.interface import implements

from ushare.core.portlets.smart.renderers import PortletContainerRenderer
from ushare.core.portlets.smart.renderers import PortletItemRenderer
from ushare.core.portlets.smart.renderers.interfaces import IPortletContainerRenderer
from ushare.core.portlets.smart.renderers.interfaces import IPortletItemRenderer

import re

AUDIO_REGEX = re.compile(r'.mp3|.m4a|.acc|.f4a|.ogg|.oga|.mp4|.m4v|.f4v|.mov|.flv|.webm|.smil|.m3u8', re.IGNORECASE)


class ListPortletContainerRenderer(PortletContainerRenderer):
    implements(IPortletContainerRenderer)
    adapts(IPortletRenderer)

    title = "View with items wrapped in ul > li"
    template = ViewPageTemplateFile('templates/container_li.pt')
    css_class = 'portlet-container-list'


class DivPortletContainerRenderer(PortletContainerRenderer):
    implements(IPortletContainerRenderer)
    adapts(IPortletRenderer)

    title = "View with items wrapped in div > div"
    template = ViewPageTemplateFile('templates/container_div.pt')
    css_class = 'portlet-container-div'


class CarouselPortletContainerRenderer(PortletContainerRenderer):
    implements(IPortletContainerRenderer)
    adapts(IPortletRenderer)

    title = "Carousel view"
    template = ViewPageTemplateFile('templates/container_carousel.pt')
    css_class = 'carousel-container-div'

    def getTitleIdPortlet(self):
        return self.portlet.data.header.replace(" ", "-")


class ImagePortletItemRenderer(PortletItemRenderer):
    implements(IPortletItemRenderer)
    adapts(IImage)

    title = "Image view"
    template = ViewPageTemplateFile('templates/image.pt')
    css_class = 'carousel-image'


class DefaultPortletItemRenderer(PortletItemRenderer):
    implements(IPortletItemRenderer)
    adapts(IContentish)

    template = ViewPageTemplateFile('templates/default.pt')
    css_class = 'contentish-item'
