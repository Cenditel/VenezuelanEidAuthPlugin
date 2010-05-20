from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
import string

from Products.VenezuelanEidAuthPlugin.config import *

def install(self, reinstall=False):
    """Register password reset skins and add the tool"""
    directory_name = 'VenezuelanEidAuthPlugin'
    
    out = StringIO()

    # Setup the skins
    skinstool = getToolByName(self, 'portal_skins')
    if directory_name not in skinstool.objectIds():
        # We need to add Filesystem Directory Views for any directories
        # in our skins/ directory.  These directories should already be
        # configured.
        addDirectoryViews(skinstool, 'skins', product_globals)
        out.write("Added %s directory view to portal_skins\n" % directory_name)
    
    
    #By default we could also remove the portlet_login from left_slots and right_slots   
    #but this is to restrictive so we just show in doc how to do it
    #Update action linked to the "connect" link
    #change "login_form" to "choose_connection_mode"
#     mtool = getToolByName(self, "portal_membership", None)
#     #we remove the "join" action and we add another one
#     if mtool:
#         actions = mtool._actions
#         filtered = [action for action in actions if action.id != "login"]
#         if len(actions) != len(filtered):
#             mtool._actions = tuple(filtered)
#             mtool.addAction(id="login",
#                             name="Log in",
#                             action="string:${portal_url}/choose_connection_mode",
#                             condition="not: member",
#                             permission="View",
#                             category="user",
#                             visible=1,
#                             REQUEST=None
#                         )
    
    # Now we need to go through the skin configurations and insert
    # directory_name into the configurations.  Preferably, this
    # should be right after where 'custom' is placed.  Otherwise, we
    # append it to the end.
    skins = skinstool.getSkinSelections()
    for skin in skins:
        path = skinstool.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        if directory_name not in path:
            try: path.insert(path.index('custom')+1, directory_name)
            except ValueError:
                path.append(directory_name)
                
            path = string.join(path, ', ')
            # addSkinSelection will replace existing skins as well.
            skinstool.addSkinSelection(skin, path)
            out.write("Added %s to %s skin\n" % (directory_name, skin))
        else:
            out.write("Skipping %s skin, %s is already set up\n" % (
                skin, directory_name))
    
    
    #we add a property called https_address to site_properties
    portal = getToolByName(self, 'portal_url').getPortalObject()
    if not portal.portal_properties.site_properties.hasProperty('https_address'):
        portal.portal_properties.site_properties.manage_addProperty('https_address', 'https://change_this_url_but_not_the_extension/logged_in', 'string')
    
    #Add the MemberWithEid role to PAS if no exist
    if HAS_PLONEPAS:
        pas = getToolByName(self, 'acl_users', None)
        prm = pas.portal_role_manager
        if not "MemberWithEid" in prm.listRoleIds():
            out.write("Adding MemberWithEid role")
            prm.addRole("MemberWithEid", "MemberWithEid", "A member that connect with his eID card")
        else:
            out.write("MemberWithEid role already exist")

    if HAS_PLONEPAS:
        #We add the VenezuelanEidAuthPlugin in plonePas
        acl = portal.acl_users
        if not hasattr(acl, 'VenezuelanEidAuthPlugin'):
            acl.manage_addProduct['VenezuelanEidAuthPlugin'].manage_addVenezuelanEidAuthPlugin('VenezuelanEidAuthPlugin', title='VenezuelanEidAuthPlugin')

        #we activate the interfaces on the plugin
        if hasattr(acl, 'VenezuelanEidAuthPlugin'):
            plugin_obj = acl.VenezuelanEidAuthPlugin
            activatable = []
            try:
                for info in plugin_obj.plugins.listPluginTypeInfo():
                    interface = info['interface']
                    interface_name = info['id']
                    if plugin_obj.testImplements(interface):
                        activatable.append(interface_name)
                        out.write("VenezuelanEidAuthPlugin : activating: %s" % info['title'])
            except AttributeError:
                out.write('Error : VenezuelanEidAuthPlugin : it looks like you have a non-PAS acl_users folder.')
            plugin_obj.manage_activateInterfaces(activatable)
    
    return out.getvalue()
