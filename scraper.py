#!/usr/bin/env python
from config import airfare_scraper
from config import config

for c in config.configs_to_scrape:
  scraper = airfare_scraper.AirfareScraper(c, False)
  scraper.scrape()
