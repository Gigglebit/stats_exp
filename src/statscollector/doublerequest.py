#!/bin/python
import urllib2
#for i in xrange(10):
response1 = urllib2.urlopen('http://10.0.0.254:8080/stats/1/2/0/0')
response2 = urllib2.urlopen('http://10.0.0.254:8080/stats/2/1/0/0')
h1=response1.read()
print h1
print "----------------------------------"
h2=response2.read()
print h2
print "----------------------------------"
print "----------------------------------"
