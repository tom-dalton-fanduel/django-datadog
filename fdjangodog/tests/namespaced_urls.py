from django.conf.urls import url
from django.views.generic.base import View


urlpatterns = [
    url(r'^test/$', View.as_view(), name='a_namespaced_url'),
]
