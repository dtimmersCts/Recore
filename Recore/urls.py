"""
Definition of urls for Recore.
"""

import django.contrib.auth.views

from datetime import datetime
from django.conf import settings
from django.conf.urls import *
from django.contrib import admin
from django.contrib.auth import views as auth_views

import app.forms
import app.views

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()
   
urlpatterns = [
    # URL patterns to enable all views:
    # Django Auth and Google SSO URL patterns
    url(r'^login/$', django.contrib.auth.views.login,
        {
            'template_name': 'app/login.html',
            'extra_context':
            {
                'title': 'Login',
                'message': 'Welcome to the CTS Kiosk Database',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url('', include('social_django.urls', namespace='social')),
    url(r'^logout$', django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),
    # Recore main pages URL patterns
    url(r'^$', app.views.home, name='home'),
    url(r'^searchRecore$', app.views.searchRecore, name='searchRecore'),
    url(r'^clientList$', app.views.clientList, name='clientList'),
    url(r'^updateKiosk$', app.views.updateKiosk, name='updateKiosk'),
    url(r'^productionRelease$', app.views.productionRelease, name='productionRelease'),
    url(r'^newKiosk$', app.views.newKiosk, name='newKiosk'),
    url(r'^newClient$', app.views.newClient, name='newClient'),
    url(r'^retrofitKiosk$', app.views.retrofitKiosk, name='retrofitKiosk'),
    ### Removed URL pattern for removeKiosk function
    # url(r'^removeKiosk$', app.views.removeKiosk, name='removeKiosk'),
    ### End URL pattern for removeKiosk function
    url(r'^updateDatabase$', app.views.updateDatabase, name='updateDatabase'),
    url(r'^generatePDF$', app.views.generatePDF, name='generatePDF'),
    url(r'^error', app.views.error, name='error'),
    # Search Recore subviews
    url(r'^getSearchForm', app.views.getSearchForm, name='getSearchForm'),
    url(r'^searchRecoreResults', app.views.searchRecoreResults, name='searchRecoreResults'),
    # Client List subviews
    url(r'^clientList/([\w \']+)/$', app.views.clientKioskList, name='clientKioskList'),
    # CTS Production Release subviews
    url(r'^newProdRlse$', app.views.newProdRlse, name='newProdRlse'),
    url(r'^existProdRlse', app.views.existProdRlse, name='existProdRlse'),
    url(r'^createProdRlse', app.views.createProdRlse, name='createProdRlse'),
    url(r'^newProdRlseEquip', app.views.newProdRlseEquip, name='newProdRlseEquip'),
    url(r'^getSubEquip', app.views.getSubEquip, name='getSubEquip'),
    url(r'^existingSubequip', app.views.existingSubequip, name='existingSubequip'),
    url(r'^editProdRlseInfo', app.views.editProdRlseInfo, name='editProdRlseInfo'),
    url(r'^editProdRlseEquip', app.views.editProdRlseEquip, name='editProdRlseEquip'),
    url(r'^resetProdRlse', app.views.resetProdRlse, name='resetProdRlse'),
    url(r'^editExistSubequip', app.views.editExistSubequip, name='editExistSubequip'),
    url(r'^checkExistEquipRestrict', app.views.checkExistEquipRestrict, name='checkExistEquipRestrict'),
    # MT New Kiosk subviews
    url(r'^newKioskEquip', app.views.newKioskEquip, name='newKioskEquip'),
    # New Client subviews
    url(r'^newClient_addContact', app.views.newClient_addContact, name='newClient_addContact'),
    # Retrofit Kiosk subviews
    url(r'^retrofitEquip', app.views.retrofitEquip, name='retrofitEquip'),
    url(r'^retrofitKioskComplete', app.views.retrofitKioskComplete, name='retrofitKioskComplete'),
    ### Remove URL pattern for removeKiosk function subviews
    # Remove Kiosk subviews
    # url(r'^removeKiosk_deleteKiosk', app.views.removeKiosk_deleteKiosk, name='removeKiosk_deleteKiosk'),
    ### End URL pattern for removeKiosk function subviews
    # Update Database subviews
    url(r'^getDatabaseForm', app.views.getDatabaseForm, name='getDatabaseForm'),
    url(r'^kioskModelNewEquip$', app.views.kioskModelNewEquip, name='kioskModelNewEquip'),
    url(r'^kioskModelCreateEquip$', app.views.kioskModelCreateEquip, name='kioskModelCreateEquip'),
    url(r'^kioskModelNewComp$', app.views.kioskModelNewComp, name='kioskModelNewComp'),
    url(r'^kioskModelCreateComp$', app.views.kioskModelCreateComp, name='kioskModelCreateComp'),
    url(r'^kioskModelNewProd$', app.views.kioskModelNewProd, name='kioskModelNewProd'),
    url(r'^kioskModelCreateProd$', app.views.kioskModelCreateProd, name='kioskModelCreateProd'),
    url(r'^newEquipRelations', app.views.newEquipRelations, name='newEquipRelations'),
    url(r'^cancelDatabaseForm', app.views.cancelDatabaseForm, name='cancelDatabaseForm'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]

# Redirect HTTP Errors to the Error Page
handler400 = 'app.views.error'
handler403 = 'app.views.error'
handler404 = 'app.views.error'
handler500 = 'app.views.error'


# When DEBUG is turned on - sets the django debug_toolbar url pattern for development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        ]