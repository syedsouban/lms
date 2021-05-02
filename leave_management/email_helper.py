# import sendgrid
from leave_management.models import Employee, EmployeeLeaveApplication, LeaveTypes
import os
from django.conf import settings
# from sendgrid.helpers.mail import *
from django.core.mail import send_mail
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
from django.urls import resolve
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailHelper:

    @staticmethod
    def sendChangePasswordMail(params, to_email):
        try:
            ctx = Context(params)                
            html_content = render_to_string('password-change-alert.html', params)            
            return EmailHelper.sendMail(to_email,"TimeTracker - Password Change Notification", html_content)            
        except Exception as err:
            print("password-change-alert error ",err)
            return False
        return False

    @staticmethod
    def sendPasswordRecoveryMail(params, to_email):
        try:
            ctx = Context(params)                  
            html_content = render_to_string('password-recovery.html', params)            
            return EmailHelper.sendMail(to_email,"TimeTracker - Password Recovery Notification", html_content)            
        except Exception as err:
            print("password-change-alert error ",err)
            return False
        return False
    
    @staticmethod
    def sendStaffWelcomeMail(params, to_email):
        try:
            ctx = Context(params)     
            #tempPath=settings.EMAIL_TEMPLATES_DIR + '/welcome.html'
            #print('template path:', tempPath)    
            html_content = render_to_string('staff-welcome.html', params)
            #print('processed html', html_content)
            return EmailHelper.sendMail(to_email,"Welcome to TimeTracker", html_content)            
        except Exception as err:
            print("sendWelcomeMail error ",err)
            return False
        return False        
    
    @staticmethod
    def sendWelcomeMail(params, to_email):
        try:
            ctx = Context(params)     
            #tempPath=settings.EMAIL_TEMPLATES_DIR + '/welcome.html'
            #print('template path:', tempPath)    
            html_content = render_to_string('welcome.html', params)
            #print('processed html', html_content)
            return EmailHelper.sendMail(to_email,"Welcome to TimeTracker", html_content)            
        except Exception as err:
            print("sendWelcomeMail error ",err)
            return False
        return False
    
    @staticmethod
    def sendProductivityAlertMail(params, to_email):
        try:
            ctx = Context(params)     
            #tempPath=settings.EMAIL_TEMPLATES_DIR + '/welcome.html'
            #print('template path:', tempPath)    
            html_content = render_to_string('emp-productity-alert.html', params)
            #print('processed html', html_content)
            return EmailHelper.sendMail(to_email,"Bad Timesheet Alert!", html_content)            
        except Exception as err:
            print("Bad timehseet alert error ",err)
            return False
        return False

    # @staticmethod
    # def sendMail(to_email, subject, content):
        
    #     result = send_mail(subject, message=content,html_message=content,from_email = 'contact@accenflair.com',
    #     recipient_list = [to_email,'anand.t@accenflair.com'])
    #     #print('email result', result)
    #     return True if result==1 else False

    @staticmethod
    def send_leave_application_mail(params, leave_type_id, employee_id):
        ctx = Context(params)
        leave_type = LeaveTypes.objects.get(pk = leave_type_id).name
        employee = Employee.objects.get(pk = employee_id)
        email = employee.email
        full_name = employee.full_name
        params.update({
            "full_name":full_name,
            "leave_type": leave_type
        })
        html_content = render_to_string('leave_application.html', params)
        EmailHelper.sendMail(email, "Leave Application", html_content)
    
    @staticmethod
    def send_leave_status_change_mail(params, leave_id):
        ctx = Context(params)
        leave_application = EmployeeLeaveApplication.objects.select_related("employee").filter(pk = leave_id)[0]
        start_date = leave_application.start_date
        end_date = leave_application.end_date
        leave_type = LeaveTypes.objects.get(pk = leave_application.leave_type_id).name
        employee = leave_application.employee
        email = employee.email
        full_name = employee.full_name
        manager_id = employee.manager_id
        managers_mail = Employee.objects.get(pk = manager_id).email
        params.update({
            "full_name":full_name,
            "leave_type": leave_type,
            "start_date":start_date,
            "end_date":end_date
        })
        html_content = render_to_string('leave_status_change.html', params)
        EmailHelper.sendMail(email, "Leave Status Change", html_content, True, managers_mail)

    @staticmethod
    def sendMail(receiver_email, subject, content, is_html_message = True, cc = ""):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = "superstoredummy@gmail.com"
        message["To"] = receiver_email
        recepients = [receiver_email]
        if cc:
            message["Cc"] = cc
            if "," in cc:
                recepients.extend(cc.split(","))
            else:
                recepients.append(cc)
        
        
        part = MIMEText(content, "html" if is_html_message else "plain")
        
        # The email client will try to render the last part first
        message.attach(part)
        
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "superstoredummy@gmail.com"  # Enter your address
        password = "s3ndm@!l890"

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recepients, message.as_string())

    # @staticmethod
    # def sendGridMail(cls, to_email, subject, content):
    #     sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    #     from_email = Email("test@example.com")
    #     to_email = To("test@example.com")
    #     subject = "Welcome to TimeTracker"
    #     content = Content("text/html", "Dear Anand, A Test Email")
    #     mail = Mail(from_email, to_email, subject, content)
    #     response = sg.client.mail.send.post(request_body=mail.get())
    #     print(response.status_code)
    #     print(response.body)
    #     print(response.headers)
    #     return response.status_code