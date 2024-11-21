# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin

from plone import api
from zope.interface import alsoProvides

from ushare.core.utils import add_user_to_catalog
from ushare.core.utils import remove_user_from_catalog


class addUserPropertiesCatalog(BrowserView):
    """ Rebuild the OMEGA13 repoze.catalog for specific user properties data

        For default, we use the mutable_properties (users who have entered into communities)

        Path directo del plugin:
        acl_users/plugins/manage_plugins?plugin_type=IPropertiesPlugin

        En ACL_USERS / LDAP / Properties / Active Plugins ha de estar ordenado así:
          mutable_properties / auto_group / ldapaspb

        But really, we use the most preferent plugin
        If the most preferent plugin is:
           mutable_properties --> users who have entered into communities
           ldap --> users in LDAP
    """

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        if 'users' in self.request.form:
            portal = api.portal.get()
            plugins = portal.acl_users.plugins.listPlugins(IPropertiesPlugin)

            # We use the most preferent plugin
            # If the most preferent plugin is:
            #    mutable_properties --> users who have entered into communities
            #    ldap --> users in LDAP
            pplugin = plugins[-1][1]

            usersid = self.request.form['users'].split(',')
            msg = ''
            for userid in usersid:
                user_properties = pplugin.enumerateUsers(id=userid)
                for user in user_properties:
                    if user['id'] == userid:
                        user.update(dict(username=user['id']))
                        if 'title' in user:
                            user.update(dict(fullname=user['title']))
                        elif 'fullname' in user:
                            user.update(dict(fullname=user['fullname']))
                        elif 'sn' in user:
                            user.update(dict(fullname=user['sn']))
                        else:
                            user.update(dict(fullname=user['cn']))

                        user_obj = api.user.get(user['id'])

                        if user_obj:
                            add_user_to_catalog(user_obj, user)
                            print('Updated properties catalog for ' + user['id'])
                            msg += user['id'] + ': Ok\n'

                        else:
                            print('No user found in user repository (LDAP) ' + user['id'])
                            msg += user['id'] + ': Error\n'

            print('Finish add_user_catalog')
            if msg != '':
                self.context.plone_utils.addPortalMessage(msg, 'info')


class removeUserPropertiesCatalog(BrowserView):
    """ Remove specific user in catalog.
    """

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        if 'users' in self.request.form:
            users = self.request.form['users'].split(',')

            msg = ''
            for username in users:
                remove_user_from_catalog(username)
                print('Delete properties catalog for ' + username)
                msg += username + ': Ok\n'

            print('Finish remove_user_catalog')
            if msg != '':
                self.context.plone_utils.addPortalMessage(msg, 'info')
