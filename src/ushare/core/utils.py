# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from ushare.core import HAS_PAM
from ushare.core import IAMULEARN
from ushare.core.controlpanel.core import IUshareCoreControlPanelSettings
from ushare.core.directory import METADATA_USER_ATTRS
from BeautifulSoup import BeautifulSoup
from plone import api
from plone.registry.interfaces import IRegistry
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PlonePAS.tools.memberdata import MemberData
from repoze.catalog.query import Eq
from souper.interfaces import ICatalogFactory
from souper.soup import get_soup
from souper.soup import Record
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory

import json
import logging
import unicodedata
import requests
import io


from OFS.Image import Image
from mrs5.max.utilities import IMAXClient
from OFS.Image import Image
from time import time
import urllib
import PIL
from PIL import ImageOps
from cStringIO import StringIO


logger = logging.getLogger(__name__)

PLMF = MessageFactory('plonelocales')

if HAS_PAM:
    from plone.app.multilingual.interfaces import ITranslationManager


def base_config():
    """ Funcio que retorna les configuracions del controlpanel """
    registry = queryUtility(IRegistry)
    return registry.forInterface(IUshareCoreControlPanelSettings)


def havePermissionAtRoot():
    """Funcio que retorna si es Editor a l'arrel"""
    proot = portal()
    pm = api.portal.get_tool(name='portal_membership')
    sm = getSecurityManager()
    user = pm.getAuthenticatedMember()

    return sm.checkPermission('Modify portal content', proot) or \
        ('Manager' in user.getRoles()) or \
        ('Site Administrator' in user.getRoles())
    # WebMaster used to have permission here, but not anymore since uLearn
    # makes use of it
    # ('WebMaster' in user.getRoles()) or \


def portal_url():
    """Get the Plone portal URL out of thin air without importing fancy
       interfaces and doing multi adapter lookups.
    """
    return portal().absolute_url()


def portal():
    """Get the Plone portal object out of thin air without importing fancy
       interfaces and doing multi adapter lookups.
    """
    return getSite()


def abrevia(summary, sumlenght):
    """ Retalla contingut de cadenes
    """
    bb = ''

    if sumlenght < len(summary):
        bb = summary[:sumlenght]

        lastspace = bb.rfind(' ')
        cutter = lastspace
        precut = bb[0:cutter]

        if precut.count('<b>') > precut.count('</b>'):
            cutter = summary.find('</b>', lastspace) + 4
        elif precut.count('<strong>') > precut.count('</strong>'):
            cutter = summary.find('</strong>', lastspace) + 9
        bb = summary[0:cutter]

        if bb.count('<p') > precut.count('</p'):
            bb += '...</p>'
        else:
            bb = bb + '...'
    else:
        bb = summary

    try:
        return BeautifulSoup(bb.decode('utf-8', 'ignore')).prettify()
    except:
        return BeautifulSoup(bb).prettify()


def abreviaPlainText(summary, sumlenght):
    """ Retalla contingut de cadenes
    """
    bb = ''

    if sumlenght < len(summary):
        bb = summary[:sumlenght]

        lastspace = bb.rfind(' ')
        bb = bb[0:lastspace]
    else:
        bb = summary

    return bb


def pref_lang():
    """ Extracts the current language for the current user. """
    lt = api.portal.get_tool(name='portal_languages')
    return lt.getPreferredLanguage()


def link_translations(items):
    """
        Links the translations with the declared items with the form:
        [(obj1, lang1), (obj2, lang2), ...] assuming that the first element
        is the 'canonical' (in PAM there is no such thing).
    """
    # Grab the first item object and get its canonical handler
    canonical = ITranslationManager(items[0][0])

    for obj, language in items:
        if not canonical.has_translation(language):
            canonical.register_translation(language, obj)


def get_safe_member_by_id(username):
    """Gets user info from the repoze.catalog based user properties catalog.
       This is a safe implementation for getMemberById portal_membership to
       avoid useless searches to the LDAP server. It gets only exact matches (as
       the original does) and returns a dict. It DOES NOT return a Member
       object.
    """
    portal = api.portal.get()
    soup = get_soup('user_properties', portal)
    username = username.lower()
    records = [r for r in soup.query(Eq('id', username))]
    if records:
        properties = {}
        for attr in records[0].attrs:
            if records[0].attrs.get(attr, False):
                properties[attr] = records[0].attrs[attr]

        # Make sure that the key 'fullname' is returned anyway for it's used in
        # the wild without guards
        if 'fullname' not in properties:
            properties['fullname'] = ''

        return properties
    else:
        # No such member: removed?  We return something useful anyway.
        return {'username': username, 'description': '', 'language': '',
                'home_page': '', 'name_or_id': username, 'location': '',
                'fullname': ''}


def get_all_user_properties(user):
    """
        Returns a mapping with all the defined user profile properties and its values.

        The properties list includes all properties defined on any profile extension that
        is currently registered. For each of this properties, the use object is queried to
        retrieve the value. This may result in a empty value if that property is not set, or
        the value of the property provided by any properties PAS plugin.

        NOTE: Mapped LDAP atrributes will be retrieved and returned on this mapping if any.

    """
    user_properties_utility = getUtility(ICatalogFactory, name='user_properties')
    attributes = user_properties_utility.properties + METADATA_USER_ATTRS

    try:
        extender_name = api.portal.get_registry_record('ushare.core.controlpanel.core.IUshareCoreControlPanelSettings.user_properties_extender')
    except:
        extender_name = ''

    if extender_name:
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            #attributes_antiguo = attributes + extended_user_properties_utility.properties
            attributes.extend([element for element in extended_user_properties_utility.properties if element not in attributes])
    mapping = {}
    for attr in attributes:
        # OJO revisar este if mas adelante, no estaba en plone4
        if attr != 'username':
            try:
                value = user.getProperty(attr)
                if isinstance(value, str) or isinstance(value, unicode) or isinstance(value, bool) or isinstance(value, list) or isinstance(value, tuple):
                    mapping.update({attr: value})
            except:
                portal = api.portal.get()
                logger.error('ERROR PROPERTY {} in USER_PROPERTIES {} ALL_ATTRIBUTES {} EXTENDED_PROPERTIES {} PORTAL {} '.format(attr, extender_name, attributes, extended_user_properties_utility.properties, portal))
                pass

    return mapping


def remove_user_from_catalog(username):
    portal = api.portal.get()
    soup = get_soup('user_properties', portal)
    exists = [r for r in soup.query(Eq('id', username))]
    if exists:
        user_record = exists[0]
        del soup[user_record]

    if IAMULEARN:
        extender_name = api.portal.get_registry_record('ushare.core.controlpanel.core.IUshareCoreControlPanelSettings.user_properties_extender')
        # Make sure that, in fact we have such a extender in place
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_soup = get_soup(extender_name, portal)
            exist = []
            exist = [r for r in extended_soup.query(Eq('id', username))]
            if exist:
                extended_user_record = exist[0]
                del extended_soup[extended_user_record]


def add_user_to_catalog(user, properties={}, notlegit=False, overwrite=False):
    """ Adds a user to the user catalog

        As this method can be called from multiple places, user parameter can be
        a MemberData wrapped user, a PloneUser object or a plain (string) username.

        If the properties parameter is ommitted, only a basic record identifying the
        user will be created, with no extra properties.

        The 'notlegit' argument is used when you can add the user for its use in
        the ACL user search facility. If so, the user would not have
        'searchable_text' and therefore not searchable. It would have an extra
        'notlegit' index.

        The overwrite argument controls whether an existing attribute value on a user
        record will be overwritten or not by the incoming value. This is in order to protect
        user-provided values via the profile page.


    """
    portal = api.portal.get()
    soup = get_soup('user_properties', portal)
    if isinstance(user, MemberData):
        username = user.getUserName()
    elif isinstance(user, PloneUser):
        username = user.getUserName()
    else:
        username = user
    # add lower to take correct user_soup
    username = username.lower()
    exist = [r for r in soup.query(Eq('id', username))]
    user_properties_utility = getUtility(ICatalogFactory, name='user_properties')

    if exist:
        user_record = exist[0]
        # Just in case that a user became a legit one and previous was a nonlegit
        user_record.attrs['notlegit'] = False
    else:
        record = Record()
        record_id = soup.add(record)
        user_record = soup.get(record_id)
        # If the user do not exist, and the notlegit is set (created by other
        # means, e.g. a test or ACL) then set notlegit to True This is because
        # in non legit mode, maybe existing legit users got unaffected by it
        if notlegit:
            user_record.attrs['notlegit'] = True

    if isinstance(username, str):
        user_record.attrs['username'] = username.decode('utf-8')
        user_record.attrs['id'] = username.decode('utf-8')
    else:
        user_record.attrs['username'] = username
        user_record.attrs['id'] = username

    property_different_value = False
    if properties:
        for attr in user_properties_utility.properties + METADATA_USER_ATTRS:
            has_property_definition = attr in properties
            property_empty_or_not_set = user_record.attrs.get(attr, u'') == u''

            if has_property_definition:
                if isinstance(properties[attr], str):
                    property_different_value = user_record.attrs.get(attr, u'') != properties[attr].decode('utf-8')
                else:
                    property_different_value = user_record.attrs.get(attr, u'') != properties[attr]

            if has_property_definition and (property_empty_or_not_set or overwrite or property_different_value):
                if isinstance(properties[attr], str):
                    user_record.attrs[attr] = properties[attr].decode('utf-8')
                elif isinstance(properties[attr], bool):
                    user_record.attrs[attr] = str(properties[attr]).decode('utf-8')
                else:
                    user_record.attrs[attr] = properties[attr]

    # If notlegit mode, then reindex without setting the 'searchable_text' This
    # is because in non legit mode, maybe existing legit users got unaffected by
    # it
    if notlegit:
        soup.reindex(records=[user_record])
        return

    # Build the searchable_text field for wildcard searchs
    user_record.attrs['searchable_text'] = ''
    for key in user_properties_utility.properties:
        if user_record.attrs.get(key, False) and 'check_' not in key:
            checkKey = 'check_' + key
            hasCheck = checkKey in user_record.attrs
            if not hasCheck or (hasCheck and user_record.attrs[checkKey] != 'False'):
                user_record.attrs['searchable_text'] += unicodedata.normalize('NFKD', user_record.attrs[key]).encode('ascii', errors='ignore') + ' '
    soup.reindex(records=[user_record])

    # If uLearn is present, then lookup for a customized set of fields and its
    # related soup. The soup has the form 'user_properties_<client_name>'. This
    # feature is currently restricted to uLearn but could be easily backported
    # to Base. The setting that makes the extension available lives in:
    # 'ushare.core.controlpanel.core.IUshareCoreControlPanelSettings.user_properties_extender'
    if IAMULEARN:
        extender_name = api.portal.get_registry_record('ushare.core.controlpanel.core.IUshareCoreControlPanelSettings.user_properties_extender')
        # Make sure that, in fact we have such a extender in place
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_soup = get_soup(extender_name, portal)
            exist = []
            exist = [r for r in extended_soup.query(Eq('id', username))]
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)

            if exist:
                extended_user_record = exist[0]
            else:
                record = Record()
                record_id = extended_soup.add(record)
                extended_user_record = extended_soup.get(record_id)

            if isinstance(username, str):
                extended_user_record.attrs['username'] = username.decode('utf-8')
                extended_user_record.attrs['id'] = username.decode('utf-8')
            else:
                extended_user_record.attrs['username'] = username
                extended_user_record.attrs['id'] = username

            property_different_value = False
            if properties:
                for attr in extended_user_properties_utility.properties:
                    has_property_definition = attr in properties
                    property_empty_or_not_set = extended_user_record.attrs.get(attr, u'') == u''

                    if has_property_definition:
                        if isinstance(properties[attr], str):
                            property_different_value = extended_user_record.attrs.get(attr, u'') != properties[attr].decode('utf-8')
                        else:
                            property_different_value = extended_user_record.attrs.get(attr, u'') != properties[attr]

                    # Only update it if user has already not property set or it's empty
                    if has_property_definition and (property_empty_or_not_set or overwrite or property_different_value):
                        if isinstance(properties[attr], str):
                            extended_user_record.attrs[attr] = properties[attr].decode('utf-8')
                        elif isinstance(properties[attr], bool):
                            extended_user_record.attrs[attr] = str(properties[attr]).decode('utf-8')
                        else:
                            extended_user_record.attrs[attr] = properties[attr]

            # Update the searchable_text of the standard user record field with
            # the ones in the extended catalog
            user_record.attrs['searchable_text'] = ''
            if hasattr(extended_user_properties_utility, 'public_properties'):
                for key in extended_user_properties_utility.public_properties:
                    if extended_user_record.attrs.get(key, False) and 'check_' not in key:
                        checkKey = 'check_' + key
                        hasCheck = checkKey in extended_user_record.attrs
                        if not hasCheck or (hasCheck and extended_user_record.attrs[checkKey] != 'False'):
                            value = extended_user_record.attrs[key]

                            if isinstance(value, list) or isinstance(value, tuple):
                                value = ' '.join(value)

                            # Value widget select multiple
                            if value[0:2] == '[[' and value[-2:] == ']]':
                                value = ' '.join(json.loads(value)[0])

                            if isinstance(value, unicode):
                                user_record.attrs['searchable_text'] += ' ' + unicodedata.normalize('NFKD', value).encode('ascii', errors='ignore')
                            else:
                                user_record.attrs['searchable_text'] += ' ' + value
            else:
                for key in extended_user_properties_utility.properties:
                    if extended_user_record.attrs.get(key, False) and 'check_' not in key:
                        checkKey = 'check_' + key
                        hasCheck = checkKey in extended_user_record.attrs
                        if not hasCheck or (hasCheck and extended_user_record.attrs[checkKey] != 'False'):
                            user_record.attrs['searchable_text'] += unicodedata.normalize('NFKD', extended_user_record.attrs[key]).encode('ascii', errors='ignore') + ' '

            # Save for free the extended properties in the main user_properties soup
            # for easy access with one query
            property_different_value = False
            if properties:
                for attr in extended_user_properties_utility.properties:
                    has_property_definition = attr in properties
                    property_empty_or_not_set = user_record.attrs.get(attr, u'') == u''

                    if has_property_definition:
                        if isinstance(properties[attr], str):
                            property_different_value = user_record.attrs.get(attr, u'') != properties[attr].decode('utf-8')
                        else:
                            property_different_value = user_record.attrs.get(attr, u'') != properties[attr]

                    # Only update it if user has already not property set or it's empty
                    if has_property_definition and (property_empty_or_not_set or overwrite or property_different_value):
                        if isinstance(properties[attr], str):
                            user_record.attrs[attr] = properties[attr].decode('utf-8')
                        elif isinstance(properties[attr], bool):
                            user_record.attrs[attr] = str(properties[attr]).decode('utf-8')
                        else:
                            user_record.attrs[attr] = properties[attr]

            soup.reindex(records=[user_record])
            extended_soup.reindex(records=[extended_user_record])


def reset_user_catalog():
    portal = api.portal.get()
    soup = get_soup('user_properties', portal)
    soup.clear()


def reset_group_catalog():
    portal = api.portal.get()
    soup = get_soup('ldap_groups', portal)
    soup.clear()


def json_response(func):
    """ Decorator to transform the result of the decorated function to json.
        Expect a list (collection) that it's returned as is with response 200 or
        a dict with 'data' and 'status_code' as keys that gets extracted and
        applied the response.
    """
    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, 'request', None)
        request.response.setHeader(
            'Content-Type',
            'application/json; charset=utf-8'
        )
        result = func(*args, **kwargs)
        if isinstance(result, list):
            request.response.setStatus(200)
            return json.dumps(result, indent=2, sort_keys=True)
        else:
            request.response.setStatus(result.get('status_code', 200))
            return json.dumps(result.get('data', result), indent=2, sort_keys=True)

    return decorator


def convertSquareImage(image_file):
    CONVERT_SIZE = (250, 250)
    try:
        image = PIL.Image.open(image_file)
    except:
        portrait_url = portal_url() + '/++theme++ulearn5/assets/images/defaultUser.png'
        imgData = requests.get(portrait_url).content
        image = PIL.Image.open(io.BytesIO(imgData))
        image.filename = 'defaultUser'

    format = image.format
    mimetype = 'image/%s' % format.lower()

    result = ImageOps.fit(image, CONVERT_SIZE, method=PIL.Image.ANTIALIAS, centering=(0.5, 0.5))

    # Bypass CMYK problem in conversion
    if result.mode not in ["1", "L", "P", "RGB", "RGBA"]:
        result = result.convert("RGB")

    new_file = StringIO()
    result.save(new_file, format, quality=88)
    new_file.seek(0)

    return new_file, mimetype

def add_portrait_user(user):
    """ Esta función le pide al max la foto de perfil del usuario
        la añade al portrait de plone y guarda en un soup si es la de por defecto o no
    """
    id = user.id
    maxclient, settings = getUtility(IMAXClient)()
    foto = maxclient.people[id].avatar
    imageUrl = foto.uri + '/large'

    portrait = urllib.urlretrieve(imageUrl)

    scaled, mimetype = convertSquareImage(portrait[0])
    portrait = Image(id=id, file=scaled, title=id)

    portal = api.portal.get()
    membertool = api.portal.get_tool(name='portal_memberdata')
    membertool._setPortrait(portrait, str(id))
    import transaction
    transaction.commit()

    member_info = get_safe_member_by_id(id)
    if member_info.get('fullname', False) \
       and member_info.get('fullname', False) != id \
       and isinstance(portrait, Image) and portrait.size != 3566 and portrait.size != 6186:
        portrait_user = True
        # 3566 is the size of defaultUser.png I don't know how get image
        # title. This behavior is reproduced in profile portlet. Ahora tambien 6186
    else:
        portrait_user = False

    soup_users_portrait = get_soup('users_portrait', portal)
    exist = [r for r in soup_users_portrait.query(Eq('id_username', id))]
    if exist:
        user_record = exist[0]
        user_record.attrs['id_username'] = id
        user_record.attrs['portrait'] = portrait_user
    else:
        record = Record()
        record_id = soup_users_portrait.add(record)
        user_record = soup_users_portrait.get(record_id)
        user_record.attrs['id_username'] = id
        user_record.attrs['portrait'] = portrait_user
    soup_users_portrait.reindex(records=[user_record])
