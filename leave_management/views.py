from django.db.models.manager import Manager
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *

class LeaveApplicationView(APIView):
    serializer_class = EmployeeLeaveApplicationSerializer
    def get_queryset(self):
        queryset = models.EmployeeLeaveApplication.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            request_serializer = LeaveApplicationGetSerializer(context = {'request':request}, data = {})
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
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def patch(self, request, *args, **kwargs):
        emp_id = request.query_params.get("emp_id")
        mgr_id = request.query_params.get("mgr_id")
        leave_id = request.query_params.get("leave_id")

    