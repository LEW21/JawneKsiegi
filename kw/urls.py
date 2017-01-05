from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^konta/$', views.accounts, name='accounts'),
	url(r'^konta/([\w.\-]+)/$', views.account, name='account'),
	url(r'^konta/([\w.\-]+)/dokumenty/([a-zA-Z0-9\-]+)/$', views.doc, name='doc'),
	url(r'^konta/([\w.\-]+)/dokumenty/([a-zA-Z0-9\-]+)/([^/]+)$', views.attachment, name='attachment'),
]
