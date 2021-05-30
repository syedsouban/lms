from .models import Employee

def get_manager_by_employee(employee):
    manager_id = employee.manager_id
    managers = Employee.objects.get(pk = manager_id)
    return managers