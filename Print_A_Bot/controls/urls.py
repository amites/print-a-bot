from django.conf.urls import url
from controls.views import home, MovementView, LightsView


urlpatterns = [
    url(r'^movement$', MovementView.as_view(), name='movement'),
    url(r'^lights$', LightsView.as_view(), name='lights'),
    url(r'^$', home, name='home'),
]