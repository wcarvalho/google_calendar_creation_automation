"""
    read.py by Wilka Carvalho
    This function loads events from your google calendar between two times.
    It then creates on object with a list of dates, and each date contains information about the events on that date. E.g.,
    {'days': [{'date': '5/22',
           'day': 1,
           'events': [{'calendar': 'cal1',
                       'summary': 'watch',
                       'time': '04:00'},
                      {'calendar': 'cal2',
                       'summary': 'read',
                       'time': '18:00'}]},
          {'date': '5/24',
           'day': 3,
           'events': [{'calendar': 'cal2',
                       'summary': 'read',
                       'time': '18:00'}]}
    }
    This is either printed out or saved to a yaml file. 
"""
# python utils
import yaml
import pprint
import argparse

# Google
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# date utilities
from pytz import timezone
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

# this library
from lib import get_calendars_info, setup_calendar
from read import load_events, display_events

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start", default=None, help="start time. format: month/day/year hour:minute, e.g. 5/20/2018 5:34. If nothing set, will use current time.")
parser.add_argument("-e", "--end", default=None, help="end time. format: month/day/year hour:minute, e.g. 5/20/2018 5:34. If nothing set, will use end of current day.")
parser.add_argument("-t", "--timezone", default="US/Pacific")
parser.add_argument("-v", "--verbose", action='store_true')
args = parser.parse_args()

tz = timezone(args.timezone)

format = "%m/%d/%Y %H:%M"

if args.start: 
    start = datetime.strptime(args.start, format).replace(tzinfo=tz).isoformat()
else: 
    start = datetime.now(tz=tz).isoformat()
if args.end: 
    end = datetime.strptime(args.end, format).replace(tzinfo=tz).isoformat()
else:
    # end = parse(start) + relativedelta(days=+1)
    # end = str(end.replace(hour=0,minute=0,tzinfo=tz))
    raise RuntimeError("Not yet implemented when don't set `--end`")

service = setup_calendar()
calendars = get_calendars_info(service)
all_events = load_events(service, calendars, start, end)

if args.verbose: display_events(all_events, start, end, tz, args.raw)