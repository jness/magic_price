from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'deck_price.views.index'),
    url(r'^gatherer/(.*)$', 'deck_price.views.gatherer_lookup'),
)
