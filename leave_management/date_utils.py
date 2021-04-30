def do_date_ranges_overlap(date1_start, date1_end, date2_start, date2_end):
    return (date1_start>=date2_start and date1_start <=date2_end) or (date2_start>=date1_start and date2_start <=date1_end)