from django.conf.urls import patterns, url
from customers import views

urlpatterns = patterns('',
    url(r'store/nearby/(?P<latitude>.+)/(?P<longitude>.+)/(?P<proximity>.+)/$', views.StoreListView.as_view()),
    url(r'store/nearby/(?P<latitude>.+)/(?P<longitude>.+)/$', views.StoreListView.as_view()),
    url(r'store/hours/(?P<store_id>.+)/$', views.OpeningHoursListView.as_view()),
    url(r'store/holiday/(?P<store_id>.+)/$', views.HolidayPeriodListView.as_view()),
    url(r'store/(?P<id>.+)/$', views.StoreListView.as_view()),

    url(r'food/store/(?P<store_id>.+)/$', views.FoodListView.as_view()),
    url(r'food/(?P<id>.+)/$', views.FoodListView.as_view()),

    url(r'order/price/$', views.OrderPriceView.as_view()),
    url(r'order/paid/(?P<id>.+)/$', views.OrderView.as_view()),
    url(r'order/update/(?P<id>.+)/(?P<status>.+)/$', views.OrderView.as_view()),
    url(r'order/(?P<id>.+)/$', views.OrderView.as_view()),
    url(r'order/$', views.OrderView.as_view()),

    url(r'token/$', views.UserTokenView.as_view()),

    url(r'user/$', views.UserView.as_view())
)
