from .models import Employee, LeaveTypes, EmployeeLeaveBalance

def get_manager_by_employee(employee):
    manager_id = employee.manager_id
    if manager_id is None:
        return None
    managers = Employee.objects.get(pk = manager_id)
    return managers

def get_special_leave_type():
    special_leave = LeaveTypes.objects.filter(name = "Special Leave")
    special_leave = special_leave[0] if len(special_leave)>0 else {}
    return special_leave

def get_lop_leave_type():
    lop_leave = LeaveTypes.objects.filter(name = "LOP Leave")
    special_leave = lop_leave[0] if len(lop_leave)>0 else {}
    return special_leave

def get_leaves_by_leave_type_and_emp_id(leave_type_id, employee):
    special_leave = get_special_leave_type()
    lop_leave = get_lop_leave_type()
    if (special_leave or lop_leave) and (leave_type_id == special_leave.leave_type_id or leave_type_id == lop_leave.leave_type_id):
        leaves = EmployeeLeaveBalance.objects.filter(employee = employee).select_related("leave_type")
    else:
        leaves = EmployeeLeaveBalance.objects.filter(employee = employee, leave_type = leave_type_id).select_related("leave_type")
    return leaves

def get_leave_balance_by_leaves(leaves):
    leave_balance = 0
    for balance_obj in leaves:
        leave_balance += balance_obj.current_balance
    return leave_balance

def get_leave_balance_by_leave_type_and_emp_id(leave_type_id, employee):
    leaves = get_leaves_by_leave_type_and_emp_id(leave_type_id, employee)
    leave_balance = get_leave_balance_by_leaves(leaves)
    return leave_balance