from django.conf.urls import url
from controls.views import home, single_lightshow, MovementView, LightsView, NewLightShowView, NewLightShowStepView


urlpatterns = [
    url(r'^movement$', MovementView.as_view(), name='movement'),
    url(r'^lights$', LightsView.as_view(), name='lights'),
    url(r'^create_lightshow$', NewLightShowView.as_view(), name='create_lightshow'),
    url(r'^create_lightshow_step$', NewLightShowStepView.as_view(), name='create_lightshow_step'),
    url(r'^lightshow/(?P<lightshow_id>[0-9]+)$', single_lightshow, name='single_lightshow'),
    url(r'^$', home, name='home'),
]