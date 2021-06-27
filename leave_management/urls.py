from django.conf.urls import url
from leave_management.views import *
from django.urls import path

urlpatterns = [
    url('credit_leaves/', credit_leaves),
    url('leave_applications', LeaveApplicationView.as_view()),
    url('leave_balances', LeaveBalanceView.as_view()),
    url('leave_credits', LeaveCreditView.as_view()),
    path("holidays",HolidaysList.as_view()),
    path("holiday/<int:pk>", HolidaysDetail.as_view()),
    path("leave_types",LeaveTypesList.as_view()),
    path("leave_type/<int:pk>", LeaveTypesDetail.as_view())
]