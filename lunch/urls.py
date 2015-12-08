from django.conf.urls import include, patterns, url

urlpatterns = patterns(
    '',
    url(
        r'^business/',
        include('business.urls')
    ),
    url(
        r'^customers/',
        include('customers.urls')
    ),
    url(
        r'^gocardless/',
        include('django_gocardless.urls')
    ),
)
