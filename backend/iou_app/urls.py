from django.urls import path
from . import views

app_name = 'iou_app'

urlpatterns = [
    path('', views.IOUListCreateView.as_view(), name='iou-list-create'),
    path('<uuid:id>/', views.IOUDetailView.as_view(), name='iou-detail'),
]
