from leave_management.models import *
from django.db.models import F
from leave_management.email_helper import EmailHelper

def credit_leaves(emp_id, leave_type_id, description, num_leaves, financial_year):
    elc = EmployeeLeaveCredit.objects.create(employee_id = emp_id, leave_type_id = leave_type_id, description = description, credited = num_leaves, financial_year = financial_year)
    curr_leave_balance = EmployeeLeaveBalance.objects.filter(employee_id = emp_id, leave_type_id = leave_type_id, financial_year = financial_year)
    status = False
    if not curr_leave_balance:
        status = EmployeeLeaveBalance.objects.create(employee_id = emp_id, leave_type_id = leave_type_id, current_balance = num_leaves, previous_balance = num_leaves, financial_year = financial_year) 
    else:
        status = EmployeeLeaveBalance.objects.filter(employee_id = emp_id, leave_type_id = leave_type_id, financial_year = financial_year) \
        .update(previous_balance = F("current_balance"), current_balance = F("current_balance")+num_leaves)
    return status

def credit_leave_to_all_employees(leave_type_id = 2, duration = 15, financial_year = 2022, description = ""):
    from django.core.paginator import Paginator
    
    paginator = Paginator(Employee.objects.all(), 1000) # chunks of 1000, you can 
                                                    # change this to desired chunk size

    for page in range(1, paginator.num_pages + 1):
        for emp in paginator.page(page).object_list:
            status = credit_leaves(emp.employee_id, leave_type_id, description, duration, financial_year)
            print(f"Status of crediting leave for employee_id = ${emp.employee_id} is ${status}")
        print("done processing page %s" % page)
    EmailHelper.send_credit_leave_op_completion_mail()

def run(*args):
    leave_type_id = args[0][1:]
    duration = args[1][1:]
    financial_year = args[2][1:]
    description = args[3][1:]
    credit_leave_to_all_employees(leave_type_id, duration, financial_year, description)
    # credit_leaves(1,1,"",10,2021)