#!/usr/bin/env python
import urllib2
from config import airfare_scraper
from config import config

for c in config.configs_to_scrape:
  scraper = airfare_scraper.AirfareScraper(c, overwrite=False)
  scraper.scrape_all()
  result = urllib2.urlopen("http://www.andrewchen.us/clearmemcache").read()
  print "Clear memcache result: ", result
