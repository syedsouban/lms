from datetime import datetime
from django.http import request
from rest_framework import serializers
from .models import *
from datetime import date

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"

class LeaveTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTypes
        fields = "__all__"

class EmployeeLeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLeaveBalance
        fields = "__all__"


class EmployeeLeaveApplicationSerializer(serializers.ModelSerializer):
    # employee =  serializers.PrimaryKeyRelatedField(queryset = Employee.objects.all())
    # description =  serializers.CharField(max_length=500, allow_blank = True)
    # start_date = serializers.DateField(required = True)
    # end_date = serializers.DateField(required = True)
    # requested_on = serializers.DateTimeField()
    # modified_on = serializers.DateTimeField()
    # description =  serializers.CharField(max_length=500)
    # status = serializers.ChoiceField(choices=(["Pending","Approved","Rejected","Cancelled"]))
    
    def check_if_leaves_overlap(self, emp_id, start_date, end_date):
        query_set =  EmployeeLeaveApplication.objects.filter(employee_id = emp_id, start_date__gte = start_date, start_date__lte = end_date, end_date__gte = start_date, end_date__lte = end_date).exclude(status = "Cancelled")
        return query_set
        return False

    def validate(self, data):
        start_date = data["start_date"]
        end_date = data["end_date"]
        if start_date > end_date:
            raise serializers.ValidationError("End date cannot be before start date")
        if self.check_if_leaves_overlap(data["employee"].employee_id, start_date, end_date):
            raise serializers.ValidationError("Employee currently has some leaves in this range")
        return data
    
    def create(self, validated_data):
        return EmployeeLeaveApplication.objects.create(**validated_data)
    
    # def update(self, instance, validated_data): 
    #     instance.status = validated_data.get('status')
    #     instance.save()
    #     return instance

    class Meta:
        model = EmployeeLeaveApplication
        fields = "__all__"

class LeaveApplicationGetSerializer(serializers.Serializer):
    
    emp_id = serializers.IntegerField(required = False)
    mgr_id = serializers.IntegerField(required = False)
    
    def custom_validator(self, data):
        emp_id = data.get("emp_id")
        mgr_id = data.get("mgr_id")
        if mgr_id and emp_id:
            raise serializers.ValidationError("Only one of mgr_id or emp_id must be passed")
        if not mgr_id and not emp_id:
            raise serializers.ValidationError("Either one of mgr_id or emp_id must be passed")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.custom_validator(attrs)
        return attrs

class LeaveApplicationUpdateSerializer(LeaveApplicationGetSerializer):
    leave_id = serializers.IntegerField(required = True)
    status = serializers.ChoiceField(choices=(["Pending","Approved","Rejected","Cancelled"]), required = True)

    def custom_validator(self, data):
        super().custom_validator(data)
        emp_id = data.get("emp_id")
        mgr_id = data.get("mgr_id")
        status = data.get("status")
        leave_id = data.get("leave_id")
        if emp_id and status not in ["Cancelled"]:
            raise serializers.ValidationError("Employee can only cancel an already applied leave")
        if mgr_id and status not in ["Approved", "Rejected"]:
            raise serializers.ValidationError("Manager can only approve or reject a leave")
        employee_rows = EmployeeLeaveApplication.objects.select_related("employee").filter(pk = leave_id)
        if len(employee_rows) == 1 and mgr_id:
            if employee_rows[0].status == "Cancelled":
                raise serializers.ValidationError("Employee has already cancelled the leave!")
            actual_manager_id = employee_rows[0].employee.manager_id
            if mgr_id!=actual_manager_id:
                raise serializers.ValidationError("Employee's manager does not match")
            
        elif len(employee_rows) == 1 and emp_id:
            actual_employee_id = employee_rows[0].employee.pk
            if emp_id!=actual_employee_id:
                raise serializers.ValidationError("This leave corresponds to a different employee")    
        else:
            raise serializers.ValidationError("Either leave or employee does not exists")
        
            
    
