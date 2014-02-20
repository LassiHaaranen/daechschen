from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

from badge.views import user_course_view, user_course_summary_view, toggle_badges

admin.autodiscover()

urlpatterns = patterns('',
    (r'^user/toggle_badges/$', toggle_badges),
	(r'^user/course/$', user_course_view),
    (r'^user/course/summary/$', user_course_summary_view),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
   )

