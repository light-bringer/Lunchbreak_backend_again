from django.conf.urls import patterns, url
from lunch import views

urlpatterns = patterns('',
    url(r'stores/nearby/(?P<latitude>.+)/(?P<longitude>.+)/(?P<proximity>.+)/$', views.StoreListView.as_view()),
    url(r'stores/nearby/(?P<latitude>.+)/(?P<longitude>.+)/$', views.StoreListView.as_view()),
    url(r'stores/(?P<id>.+)/$', views.StoreListView.as_view()),

    url(r'food/store/(?P<store_id>.+)/$', views.FoodListView.as_view()),
    # This might needs to be removed later on.
    url(r'food/(?P<id>.+)/$', views.FoodListView.as_view()),
)
