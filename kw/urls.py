from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('d/<date>/konta/', views.date_accounts, name='date_accounts'),
	path('d/<date>/konta/<acc_id>/', views.date_account, name='date_account'),
	path('d/<date>/osoby/<party_id>/', views.date_party, name='date_party'),
	path('d/<date>/osoby/<party_id>/dokumenty/<doc_id>/', views.date_doc, name='date_doc'),
]
