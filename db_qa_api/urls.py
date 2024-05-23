from django.urls import path
from db_qa_api.views import QueryToSQL

urlpatterns = [
    path('get_db/',  QueryToSQL.as_view(), name='QueryToSQL'),
]
