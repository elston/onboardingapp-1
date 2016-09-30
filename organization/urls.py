from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.OrganizationList.as_view(), name="organization_list"),
    url(r'^(?P<pk>\d+)/$',
        views.OrganizationDetail.as_view(), name="detail_organization"),
    url(r'^limit/check$',
        views.check_organization_limit, name='check_organization_limit'),
]
