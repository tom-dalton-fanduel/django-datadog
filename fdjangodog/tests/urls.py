from django.conf.urls import url
from django.views.generic.base import View


urlpatterns = [
    url(r'^unnamed_path/$', View.as_view()),
    url(r'^named_path/$', View.as_view(), name='a_url_name'),
]
