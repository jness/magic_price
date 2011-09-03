from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'deck_price.views.index'),
    url(r'^gatherer/(.*)$', 'deck_price.views.gatherer_lookup'),
)

urlpatterns += staticfiles_urlpatterns()
