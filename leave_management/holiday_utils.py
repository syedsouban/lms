import datetime
import json
from leave_management.models import Holidays
from networkdays import networkdays

def do_date_ranges_overlap(date1_start, date1_end, date2_start, date2_end):
    return (date1_start>=date2_start and date1_start <=date2_end) or (date2_start>=date1_start and date2_start <=date1_end)

def get_working_days(start_date, end_date):
    
    holidays = set()        
    holidays_from_db = Holidays.objects.all()
    for holiday in holidays_from_db:
        holidays.add(holiday.date)
        
    networkdays_obj = networkdays.Networkdays(start_date,end_date,holidays)
    return networkdays_obj.networkdays()

def get_num_working_days(start_date, end_date):
    return len(get_working_days(start_date, end_date))

# print(str(get_num_working_days(datetime.date(2021,1,1), datetime.date(2021, 12, 31))))
