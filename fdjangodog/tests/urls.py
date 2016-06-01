from django.conf.urls import url
from django.http.response import HttpResponse


def null_view(request):
    return HttpResponse()


urlpatterns = [
    url(r'', null_view),
    url(r'/test', null_view),
]
