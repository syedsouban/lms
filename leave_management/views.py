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
            success = serializer.save()
            if success:
                params = {
                    "start_date":data["start_date"],
                    "end_date":data["end_date"]
                }
                schedule([EmailHelper.send_leave_application_mail], params, data["leave_type"], data["employee"])
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
        res = EmployeeLeaveApplication.objects.filter(pk = leave_id).update(status = status)
        if res:
            leave = EmployeeLeaveApplication.objects.get(pk = leave_id)
            leave_duration = (leave.end_date - leave.start_date).days
                
            if status == "Approved":
                updated_balance = F("current_balance")-leave_duration
                EmployeeLeaveBalance.objects.filter(employee = leave.employee, leave_type = leave.leave_type).update(previous_balance = F("current_balance"),current_balance = updated_balance)
            if old_status == "Approved" and (status == "Cancelled" or status == "Rejected"):
                updated_balance = F("current_balance")+leave_duration
                EmployeeLeaveBalance.objects.filter(employee = leave.employee, leave_type = leave.leave_type).update(previous_balance = F("current_balance"), current_balance = updated_balance)
                
            params = {
                    "status":status
                }
            schedule([EmailHelper.send_leave_status_change_mail], params, leave_id)
            
            return Response({"message":"Status of leave changed successfully"})
        return Response({"message":"Something went wrong"},status = 500)

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
                leave_balances = EmployeeLeaveBalance.objects.filter(employee = emp_id)
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





        
            


    