from django.test import TestCase
from users.functions import get_percentage
# Create your tests here.
class Testing(TestCase):
    def test_func(self,amount,percent):
        self.amount = amount
        self.percent = percent
        
