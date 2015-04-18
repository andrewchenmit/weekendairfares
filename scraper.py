#!/usr/bin/env python
import airfare_scraper
import config

for c in config.configs_to_scrape:
  scraper = airfare_scraper.AirfareScraper(c, False)
  scraper.scrape()
