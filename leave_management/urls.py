from django.conf.urls import url, include
from leave_management.views import LeaveApplicationView, LeaveBalanceView, credit_leaves
from rest_framework.routers import DefaultRouter


urlpatterns = [
    url('credit_leaves/', credit_leaves),
    url('leave_applications', LeaveApplicationView.as_view()),
    url('leave_balances', LeaveBalanceView.as_view()),
]