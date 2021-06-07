from django.db import models

# Create your models here.
class Employee(models.Model):
    # account = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    employee_id = models.AutoField(primary_key=True, null=False)
    full_name = models.CharField(max_length=50, null=False)
    email = models.CharField(max_length=50, null=False)    
    mobile = models.CharField(max_length=30, null=False)
    about = models.CharField(max_length=500, blank=True, null=True)
    designation = models.CharField(max_length=100)
    country = models.CharField(max_length=30, null=False)
    company_name=models.CharField(max_length=50, blank=True, null=True) 
    created_on = models.DateTimeField(blank=False, auto_now_add=True)
    modified_on = models.DateTimeField(blank=True, auto_now=True, null=True)
    created_by = models.CharField(max_length=50, blank=False)
    modified_by = models.DateTimeField(blank=True, null=True)
    manager = models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)
    max_hours_limit = models.IntegerField(default=1, blank=False, null=True)
    screenshot_interval = models.IntegerField(default=0, blank=False, null=True)
    emp_photo_interval = models.IntegerField(default=0, blank=False, null=True)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True) 

    class Meta:
        managed = True
        db_table = 'employees'

class LeaveTypes(models.Model):
    leave_type_id = models.AutoField(primary_key=True)   
    name = models.CharField(max_length=100, blank=True, null=True)    
    description =  models.CharField(max_length=500, blank=True, null=True)          
    class Meta:
        managed = True
        db_table = 'leaves_types'

class EmployeeLeaveBalance(models.Model):   
    employee =  models.ForeignKey("Employee", models.DO_NOTHING, blank=True, null=True)
    previous_balance =  models.FloatField(default=0, blank=True, null=True)  
    current_balance =  models.FloatField(default=0, blank=True, null=True)  
    leave_type = models.ForeignKey(LeaveTypes, models.DO_NOTHING,blank=True, null=True)   # Type of Leave
    financial_year = models.IntegerField(default=2020, blank=True, null=True)
    created_on = models.DateTimeField(blank=False, auto_now_add=True, null=True)
    modified_on = models.DateTimeField(blank=True, auto_now=True, null=True)
    leave_type_name = models.CharField(max_length=50, blank=True, null=True)
    employee_name = models.CharField(max_length=50, blank=True, null=True)        
    class Meta:
        managed = True
        db_table = 'emp_leaves_balance'

class EmployeeLeaveApplication(models.Model):
    STATUS = (('Pending', 'Pending'),('Approved', 'Approved'),('Rejected', 'Rejected'))
    employee =  models.ForeignKey(Employee, models.DO_NOTHING, blank=True)
    leave_id = models.AutoField(primary_key=True)   
    description =  models.CharField(max_length=500, blank=True, null=True)  
    requested_on = models.DateTimeField(blank=False, auto_now_add=True, null=True)
    modified_on = models.DateTimeField(blank=True, auto_now=True, null=True)
    start_date = models.DateField(blank=False, null=True)
    end_date = models.DateField(blank=True, null=True)
    status =  models.CharField(choices=STATUS, max_length=20, default=STATUS[0][0])
    leave_type = models.ForeignKey(LeaveTypes, models.DO_NOTHING,blank=False, null=False)
    leave_type_name = models.CharField(max_length=50, blank=True, null=True)
    employee_name = models.CharField(max_length=50, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'leaves_applications'

class EmployeeLeaveCredit(models.Model):    
    employee =  models.ForeignKey("Employee", models.DO_NOTHING, blank=True, null=True)
    leave_credit_id = models.AutoField(primary_key=True)   
    leave_type = models.ForeignKey(LeaveTypes, models.DO_NOTHING,blank=True, null=True)   # Type of Leave
    credited =  models.IntegerField(default=0, blank=True, null=True)  # No of leaves credited    
    description =  models.CharField(max_length=500, blank=True, null=True)  
    financial_year = models.IntegerField(default=2021, blank=True, null=True)  
    month_credited = models.IntegerField(default=1, blank=True, null=True) # leaves credited for which month
    credited_on = models.DateTimeField(blank=False, auto_now_add=True, null=True)
    modified_on = models.DateTimeField(blank=True, auto_now=True, null=True)        
    class Meta:
        managed = True
        db_table = 'emp_leaves_credits'

class Holidays(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False) 
    day = models.IntegerField(blank=False, null=False)
    month = models.IntegerField(blank=False, null=False)
    year = models.IntegerField(blank=False, null=False)  
    credited_on = models.DateTimeField(blank=False, auto_now_add=True, null=True)
    modified_on = models.DateTimeField(blank=True, auto_now=True, null=True)        
    class Meta:
        managed = True
        db_table = 'holidays'
