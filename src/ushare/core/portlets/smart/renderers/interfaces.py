from zope.interface import Interface


class IPortletItemRenderer(Interface):
    """
        Renders the content of a Newsletter Box Item
    """

    def getClass():
        """
            class to be rendered in the <li> element of the item
         """


class IPortletContainerRenderer(Interface):
    """
        Renders the content of a Newsletter Box Item
    """

    def getClass():
        """
            class to be rendered in the <li> element of the item
         """
