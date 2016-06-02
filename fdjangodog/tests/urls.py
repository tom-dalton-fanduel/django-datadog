from django.conf.urls import url, include
from django.views.generic.base import View


urlpatterns = [
    url(r'^unnamed_path/$', View.as_view()),
    url(r'^named_path/$', View.as_view(), name='a_url_name'),

    url(r'^namespaced_path/', include('fdjangodog.tests.namespaced_urls', namespace="a_namespace")),
]
