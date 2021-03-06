from django.conf.urls import patterns, url
from .views import SendJSONDepartmentInvite, AcceptDepartmentInvite, CancelInvite

urlpatterns = patterns('',
                       url(r'^send-json-invite/?$',
                           SendJSONDepartmentInvite.as_view(),
                           name='send-json-invite'),
                       url(r'^accept-invite/(?P<key>\w+)/?$',
                           AcceptDepartmentInvite.as_view(),
                           name='accept-invite'),
                       url(r'^cancel-invite/(?P<pk>\d+)/?$',
                           CancelInvite.as_view(),
                           name='cancel-invite'),)
