from django.conf.urls import url

from . import views

app_name = 'frontend'
urlpatterns = [
    url(
        r'^$',
        views.IndexView.as_view(),
        name='index'
    ),
    url(
        r'^search/?$',
        views.SearchView.as_view(),
        name='search'
    ),
    url(
        r'^store/(?P<pk>\d+)/?$',
        views.StoreView.as_view(),
        name='store'
    ),
    url(
        r'^store/(?P<store_id>\d+)/order/?$',
        views.OrderView.as_view(),
        name='order'
    ),
    url(
        r'^store/(?P<store_id>\d+)/order/(?P<order_id>\d+)/?$',
        views.ConfirmView.as_view(),
        name='confirm'
    ),
    url(
        r'^group/(?P<pk>\d+)/?$',
        views.GroupView.as_view(),
        name='group'
    ),
    url(
        r'^group/(?P<pk>\d+)/join/?$',
        views.GroupJoinView.as_view(),
        name='group-join'
    ),
    url(
        r'^login/?$',
        views.LoginView.as_view(),
        name='login'
    ),
    url(
        r'^logout/?$',
        views.LogoutView.as_view(),
        name='logout'
    ),
    url(
        r'^terms/?$',
        views.TermsView.as_view(),
        name='terms'
    ),
    url(
        r'^android/?$',
        views.AndroidView.as_view(),
        name='android'
    ),
    url(
        r'^ios/?$',
        views.IOSView.as_view(),
        name='ios'
    ),
]
