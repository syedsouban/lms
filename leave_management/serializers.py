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
        query_set =  EmployeeLeaveApplication.objects.filter(employee_id = emp_id, start_date__gte = start_date, start_date__lte = end_date, end_date__gte = start_date, end_date__lte = end_date)
        return query_set

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

    class Meta:
        model = EmployeeLeaveApplication
        fields = "__all__"

class LeaveApplicationGetSerializer(serializers.Serializer):
    
    def custom_validator(self):
        request = self.context['request']
        
        emp_id = request.query_params.get("emp_id")
        mgr_id = request.query_params.get("mgr_id")
        if mgr_id and emp_id:
            raise serializers.ValidationError("Only one of mgr_id or emp_id must be passed")
        if not mgr_id and not emp_id:
            raise serializers.ValidationError("Either one of mgr_id or emp_id must be passed")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        self.custom_validator()
        return attrs