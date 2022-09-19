from ast import Num
from django.test import TestCase

# Create your tests here.
mylist = ['q','e','t']

mytuple = ('q','e','t')

def q():
    return [lambda x:i*x for i in range(4)]

print(q)