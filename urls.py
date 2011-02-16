from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'retwis.views.index'),
    (r'^timeline/$', 'retwis.views.timeline'),
    (r'^logout/$', 'retwis.views.logout')
    # Example:
    # (r'^django_retwis/', include('django_retwis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
         (r'^styles/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STYLES_DIR}),
    )
