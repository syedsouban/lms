from django.test import TestCase
from .date_utils import do_date_ranges_overlap
from datetime import date

# Create your tests here.
class DateTest(TestCase):
    def test_date_ranges_overlap_true(self):
        assert do_date_ranges_overlap(date(2021,1,1),date(2021,1,30),date(2021,1,10),date(2021,2,10)) == True
    
    def test_date_ranges_overlap_false(self):
        assert do_date_ranges_overlap(date(2020,1,1),date(2020,1,30),date(2021,1,10),date(2021,2,10)) == False
