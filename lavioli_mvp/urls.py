from django.conf.urls import url, include
from django.contrib import admin

from lavioli_mvp.views import Homeview


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r"^", include('team.urls')),
    url(r"^$", Homeview.as_view()),
    url(r'^organization/', include('organization.urls')),
]
