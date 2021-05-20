from django.conf.urls import url, include
from leave_management.views import LeaveApplicationView, credit_leaves
from rest_framework.routers import DefaultRouter


urlpatterns = [
    url('credit_leaves/', credit_leaves),
    url('', LeaveApplicationView.as_view()),
]