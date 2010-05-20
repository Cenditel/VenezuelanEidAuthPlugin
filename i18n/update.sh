#i18ndude rebuild-pot --pot collective.amberjack.portlet.pot --create collective.amberjack.portlet --merge VenezuelanEidAuthPlugin-manual.pot ../
i18ndude rebuild-pot --pot VenezuelanEidAuthPlugin.pot --create venezuelaneidauthplugin ../
i18ndude sync --pot VenezuelanEidAuthPlugin.pot VenezuelanEidAuthPlugin-*.po

i18ndude rebuild-pot --pot VenezuelanEidAuthPlugin-plone.pot --create plone ../
i18ndude sync --pot VenezuelanEidAuthPlugin-plone.pot VenezuelanEidAuthPlugin-plone-*.po
