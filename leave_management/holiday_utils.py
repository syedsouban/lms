import datetime
import json
from networkdays import networkdays

def do_date_ranges_overlap(date1_start, date1_end, date2_start, date2_end):
    return (date1_start>=date2_start and date1_start <=date2_end) or (date2_start>=date1_start and date2_start <=date1_end)

def get_working_days(start_date, end_date):
    start_year = start_date.year
    end_year = end_date.year
    years = set()
    years.add(start_year)
    years.add(end_year)
    holidays = set()
    
    for year in years:
        f = open(f"./leave_management/data/holidays_{year}.json")
        holidays_in_json = json.load(f)
        for holiday in holidays_in_json:
            holidays.add(datetime.datetime.strptime(holiday.get("date"), "%Y-%m-%d").date())
    networkdays_obj = networkdays.Networkdays(start_date,end_date,holidays)
    return networkdays_obj.networkdays()

def get_num_working_days(start_date, end_date):
    return len(get_working_days(start_date, end_date))

# print(str(get_num_working_days(datetime.date(2021,1,1), datetime.date(2021, 12, 31))))
