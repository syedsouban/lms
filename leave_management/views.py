from django.http.response import HttpResponseBadRequest
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from .email_helper import EmailHelper
from django.http import HttpResponse
from .jobs import schedule
from django.db.models import F

class LeaveApplicationView(APIView):
    serializer_class = EmployeeLeaveApplicationSerializer
    def get_queryset(self):
        queryset = models.EmployeeLeaveApplication.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            request_serializer = LeaveApplicationGetSerializer(data = request.query_params)
            if not request_serializer.is_valid():
                return Response(request_serializer.errors, status=400)
            emp_id = request.query_params.get("emp_id")
            mgr_id = request.query_params.get("mgr_id")
            if emp_id:
                leaves = EmployeeLeaveApplication.objects.filter(employee=emp_id)
                serializer = EmployeeLeaveApplicationSerializer(leaves, many = True)
            elif mgr_id:
                reportee_ids = Employee.objects.filter(manager=mgr_id).values('employee_id')
                leaves = EmployeeLeaveApplication.objects.filter(employee_id__in=reportee_ids)
                serializer = EmployeeLeaveApplicationSerializer(leaves, many = True)
        except:
            import traceback
            print(traceback.format_exc())
            return Response({"message":"Something went wrong!"},status=500)

        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        serializer = EmployeeLeaveApplicationSerializer(data=data)
        if serializer.is_valid():
            leave_applications = serializer.save()
            if leave_applications:
                serializer = EmployeeLeaveApplicationSerializer(leave_applications, many = True)
                for leave_application in leave_applications:
                    schedule([EmailHelper.send_leave_application_mail], {"start_date":leave_application.start_date, "end_date":leave_application.end_date},
                     leave_application.leave_type.leave_type_id, leave_application.employee.pk)
                return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def patch(self, request, *args, **kwargs):
        request_serializer = LeaveApplicationUpdateSerializer(data = request.query_params)
        if not request_serializer.is_valid():
            return Response(request_serializer.errors, status=400)
        leave_id = request.query_params.get("leave_id")
        old_status = EmployeeLeaveApplication.objects.get(pk = leave_id).status
        status = request.query_params.get("status")
        if old_status == status:
            return Response({"message":"This leave is already set to the same status"}, status=400)
        leave = EmployeeLeaveApplication.objects.get(pk = leave_id)
        leave_duration = (leave.end_date - leave.start_date).days + 1
        balance = get_leave_balance_by_leave_type_and_emp_id(leave.leave_type_id, leave.employee_id)
        lop_leave = get_lop_leave_type()
        if leave.leave_type_id == lop_leave.leave_type_id:
            res = EmployeeLeaveApplication.objects.filter(pk = leave_id).update(status = status)
            if res:
                return Response({"message":"Status of leave changed successfully"})
            else:
                return Response({"message":"Something went wrong"}, 500)
        if leave_duration > balance:
            return Response({"message":"Balance not availabe"}, status = 400)    
        if status == "Approved":
            updated_balance = F("current_balance")-leave_duration
            res = EmployeeLeaveBalance.objects.filter(employee = leave.employee, leave_type = leave.leave_type).update(previous_balance = F("current_balance"),current_balance = updated_balance)
        if old_status == "Approved" and (status == "Cancelled" or status == "Rejected"):
            updated_balance = F("current_balance")+leave_duration
            res = EmployeeLeaveBalance.objects.filter(employee = leave.employee, leave_type = leave.leave_type).update(previous_balance = F("current_balance"), current_balance = updated_balance)
        if res or (status == "Cancelled" or status == "Rejected"):
            EmployeeLeaveApplication.objects.filter(pk = leave_id).update(status = status)
        params = {
                "status":status
            }
        schedule([EmailHelper.send_leave_status_change_mail], params, leave_id)
        
        return Response({"message":"Status of leave changed successfully"})

class LeaveBalanceView(APIView):
    
    def get_queryset(self):
        queryset = models.EmployeeLeaveBalance.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            emp_id = request.query_params.get("emp_id")
            mgr_id = request.query_params.get("mgr_id")
            if not emp_id and not mgr_id:
                return Response(status=409)
            
            if emp_id:
                leave_balances = EmployeeLeaveBalance.objects.filter(employee = emp_id).select_related("employee").select_related("leave_types")
                for i in range(len(leave_balances)):
                    leave_balances[i].leave_type_name = leave_balances.leave_type.name
                    leave_balances[i].employee_name = leave_balances.employee.full_name
                serializer = EmployeeLeaveBalanceSerializer(leave_balances, many = True)
                return Response(serializer.data)
            elif mgr_id:
                reportee_ids = Employee.objects.filter(manager=mgr_id).values('employee_id')
                leaves = EmployeeLeaveBalance.objects.filter(employee_id__in=reportee_ids)
                serializer = EmployeeLeaveBalanceSerializer(leaves, many = True)
                return Response(serializer.data)
        except:
            import traceback
            print(traceback.format_exc())
            return Response({"message":"Something went wrong"},status = 500)

def credit_leaves(request):
    args = request.GET
    leave_type_id = args.get("leave_type_id")
    duration = args.get("duration")
    financial_year = args.get("financial_year")
    description = args.get("description")
    if not leave_type_id or not duration or not financial_year or not description:
        return HttpResponseBadRequest("Params missing")
    from subprocess import Popen
    p = Popen(f"python manage.py runscript credit_leaves --script-args ${leave_type_id} ${duration} ${financial_year} ${description}", shell=True)
    print(p)
    return HttpResponse("The script to credit leaves has been triggered! The HR will be notified once the process is completed")





        
            


    