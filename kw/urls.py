from django.conf import settings
from django.urls import path, re_path
from django.conf.urls.static import static

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('konta/', views.accounts, name='accounts'),
	path('konta/<acc_id>/', views.account, name='account'),
	path('osoby/<actor_id>/', views.actor, name='actor'),
	path('osoby/<actor_id>/dokumenty/<doc_id>/', views.doc, name='doc'),
]
