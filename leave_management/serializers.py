
import re
from rest_framework import serializers
from django.db.models import Q
from .models import *
from datetime import datetime, time, timedelta
from copy import deepcopy
from leave_management.holiday_utils import get_num_working_days, get_working_days
from .db import *

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
    def check_if_leaves_overlap(self, emp_id, start_date, end_date):
        query_set =  EmployeeLeaveApplication.objects.filter(Q(employee_id = emp_id) & (Q(start_date__gte = start_date) & Q(start_date__lte = end_date)) | (Q(end_date__gte = start_date) & Q(end_date__lte = end_date))).exclude(status__in = ["Cancelled", "Rejected"])
        return query_set

    def validate(self, data):
        start_date = data["start_date"]
        end_date = data["end_date"]
        if start_date > end_date:
            raise serializers.ValidationError("End date cannot be before start date")
        if self.check_if_leaves_overlap(data["employee"].employee_id, start_date, end_date):
            raise serializers.ValidationError("Employee currently has some leaves in this range")
        if start_date.year != end_date.year:
            raise serializers.ValidationError("Leaves being applied for more than financial year")
        requesting_days_quantity = get_num_working_days(start_date, end_date)
        lop_leave = get_lop_leave_type()
        leave_balance = get_leave_balance_by_leave_type_and_emp_id(data["leave_type"].leave_type_id, data["employee"])
        if leave_balance < requesting_days_quantity and not lop_leave.leave_type_id == data["leave_type"].leave_type_id:
            raise serializers.ValidationError("Employee does not have enough balance to avail these leaves")
        return data
    
    def create(self, validated_data):
        leaves = get_leaves_by_leave_type_and_emp_id(validated_data["leave_type"].leave_type_id, validated_data["employee"])
        start_date = validated_data["start_date"]
        end_date = validated_data["end_date"]
        working_days = get_working_days(start_date, end_date)
        requesting_days_quantity = len(working_days)
        original_leave_type_id = validated_data["leave_type"].leave_type_id
        validated_data["employee_name"] = validated_data["employee"].full_name
        start_index = 0
        end_index = -1
        data = []
        for i in range(len(leaves)):
            balance = leaves[i].current_balance
            leave_cut_for_type = balance if requesting_days_quantity > balance else requesting_days_quantity
            start_index = end_index+1
            nstart_date = working_days[start_index]
            end_index = start_index+int(leave_cut_for_type) - 1
            nend_date = working_days[end_index]
            validated_data["leave_type_name"] = leaves[i].leave_type.name
            validated_data["start_date"] = nstart_date
            validated_data["end_date"] = nend_date
            validated_data["leave_type_id"] = leaves[i].leave_type_id
            
            data.append(EmployeeLeaveApplication.objects.create(**validated_data))
            requesting_days_quantity = requesting_days_quantity - (end_index - start_index + 1)
            
        lop_leave = get_lop_leave_type()

        if requesting_days_quantity!=0 and original_leave_type_id == lop_leave.leave_type_id:
            leave_cut_for_type = requesting_days_quantity
            start_index = end_index+1
            nstart_date = working_days[start_index]
            end_index = start_index+int(leave_cut_for_type) - 1
            nend_date = working_days[end_index]
            validated_data["start_date"] = nstart_date
            validated_data["end_date"] = nend_date
            validated_data["leave_type_id"] = lop_leave.leave_type_id
            validated_data["leave_type_name"] = lop_leave.name
            data.append(EmployeeLeaveApplication.objects.create(**validated_data))
            requesting_days_quantity = requesting_days_quantity - leave_cut_for_type
            
        return data
    
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