# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implementer

ATTRIBUTE_NAME = '_notNotifyPushBy'


class INotNotifyPush(Interface):
    """ Adapt an object to this interface to manage the notify push of an object """

    def get():
        """ Return the usernames who notify push the object. """

    def add(username):
        """ Set the username that notify push the object. """

    def remove(self, username):
        """ Remove the username """


@implementer(INotNotifyPush)
class NotNotifyPush(object):
    adapts(Interface)

    def __init__(self, context):
        self.context = context
        self.not_notify_push = self.get()
        if not self.not_notify_push:
            # Initialize it
            self.not_notify_push = set([])
            setattr(self.context, ATTRIBUTE_NAME, self.not_notify_push)

    def get(self):
        return getattr(self.context, ATTRIBUTE_NAME, None)

    def add(self, username):
        username = str(username)
        self.not_notify_push.add(username)
        setattr(self.context, ATTRIBUTE_NAME, self.not_notify_push)
        self.context.reindexObject(idxs=['notNotifyPushBy'])

    def remove(self, username):
        username = str(username)
        if username in self.not_notify_push:
            self.not_notify_push.remove(username)
            setattr(self.context, ATTRIBUTE_NAME, self.not_notify_push)
            self.context.reindexObject(idxs=['notNotifyPushBy'])


@indexer(IDexterityContent)
def notNotifyPushIndexer(context):
    """Create a catalogue indexer, registered as an adapter for DX content. """
    return INotNotifyPush(context).get()
