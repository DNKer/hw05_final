from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_denied'

urlpatterns = [
    path(r'^admin/', admin.site.urls),
    path('', include('posts.urls', namespace='posts')),
    path(r'^auth/', include('users.urls', namespace='users')),
    path(r'^auth/', include('django.contrib.auth.urls')),
    path(r'^about/', include('about.urls', namespace='about')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
