from django.conf.urls import url
from django.views.generic.base import View


urlpatterns = [
    url(r'', View.as_view()),
    url(r'/test', View.as_view()),
]
