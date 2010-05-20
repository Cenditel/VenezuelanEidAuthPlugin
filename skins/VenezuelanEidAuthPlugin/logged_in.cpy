## Controller Python Script "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Initial post-login actions
##

from Products.CMFPlone import PloneMessageFactory as _
REQUEST=context.REQUEST

# If someone has something on their clipboard, expire it.
if REQUEST.get('__cp', None) is not None:
    REQUEST.RESPONSE.expireCookie('__cp', path='/')

membership_tool=context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    context.plone_utils.addPortalMessage(_(u'Login failed'))
    return state.set(status='failure')
    
member = membership_tool.getAuthenticatedMember()
login_time = member.getProperty('login_time', '2000/01/01')
initial_login = int(str(login_time) == '2000/01/01')
state.set(initial_login=initial_login)

must_change_password = member.getProperty('must_change_password', 0)
state.set(must_change_password=must_change_password)

if initial_login:
    state.set(status='initial_login')
elif must_change_password:
    state.set(status='change_password')

membership_tool.setLoginTimes()
membership_tool.createMemberArea()

#code above come from Plone
#if user is logged with his eID card, we add him a role called MemberWithEid
#a user is known as logged with his eID card when eid_username exist in the SESSION object
#beginning patch -->

#we use the key 'eid_username', because 'eid_from_http' does not mean that the user is connected, but mean that the user try to connect...
#'eid_username' = logged user, eid_from_http could cause breakage if user try to connect with his eID card, is not subscribed and try after to connect using his username and password, we MUST make sure that he do not receive the MemberWithEid role !!!

if context.REQUEST.SESSION.has_key('eid_username'):
    context.acl_users.portal_role_manager.assignRoleToPrincipal('MemberWithEid', member.getId())
else:
    context.acl_users.portal_role_manager.removeRoleFromPrincipal('MemberWithEid', member.getId())

#this is managed in VenezuelanEidAuthPlugin.py too
if not context.REQUEST.SESSION.has_key('eid_logged_in_executed'):
    context.REQUEST.SESSION.set('eid_logged_in_executed', 1)
    
#<-- end of patch
return state