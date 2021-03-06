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

# date utilities
from dateutil.parser import parse
from dateutil import tz
from datetime import datetime, timedelta

# this library
from calendar_automator.lib import *

def load_events(service, calendars, start, end, timezone, maxResults=1000):
    events = {}
    for cal in calendars:
        try:
            id = calendars[cal]['id']
            events_result = service.events().list(
                calendarId=id,
                timeMin=start.isoformat(), 
                timeMax=end.isoformat(),
                maxResults=maxResults, singleEvents=True,
                orderBy='startTime').execute()
            calendar_events = events_result.get('items', [])
            filtered = []
            # filter out all events that start before start time (mainly for events occuring at start but that started BEFORE)
            for event in calendar_events:
                ev_start, _ = read_google_event_time(event)
                ev_start = ev_start.astimezone(timezone)
                if ev_start >= start: filtered.append(event)
            events[cal] = filtered
        except Exception as e:
            print("Calendar '%s' doesn't exist" % cal)
            pass
    return events

def display_event(event, timezone):
    start, _ = read_google_event_time(event)
    start = start.astimezone(timezone)
    print("%d/%d/%d %.2d:%.2d" %(start.month, start.day, start.year, start.hour, start.minute), event['summary'])

def display_events(calendars, all_events, absolute_start, end, tz, raw=False):
    """DEPRECATED"""
    print("Printing all events between:")
    print("    %s" % absolute_start)
    print("    %s" % end)
    for cal in calendars:
        events = all_events[cal]

        print()
        print(cal)
        if not events:
            print('No upcoming events found.')
        for event in events:
            start, end = read_google_event_time(event)
            start = start.astimezone(tz)
            end = end.astimezone(tz)
            if start < absolute_start: continue

            if raw:
                # print(date.tzinfo)
                print(start, event['summary'])
            else:
                print("%d/%d/%d %.2d:%.2d" %(start.month, start.day, start.year, start.hour, start.minute), event['summary'])

def create_events_object(calendars, all_events, absolute_start, tz):

    data = {"days":[]}
    pointers = {}

    for cal in calendars:
        events = all_events[cal]

        for event in events:
            start, end = read_google_event_time(event)
            start = start.astimezone(tz)
            end = end.astimezone(tz)
            if start < absolute_start: continue

            # keep pointers to elements which are accessed by the start
            key = "%d/%d/%d" % (start.month, start.day, start.year)
            if key in pointers:
                element = pointers[key]
            else:
                element = {}
                pointers[key] = element
                data["days"].append(element)

            # element["day"] = day
            element["raw"] = str(start)
            element["date"] = "%d/%d" %(start.month, start.day)

            event_info = {
                "summary": event["summary"],
                "time": "%.2d:%.2d" %(start.hour, start.minute),
                "length": int((end-start).total_seconds()/60),
                "calendar": cal
                    }
            if "events" in element:
                element["events"].append(event_info)
            else:
                element["events"] = [event_info]

    # sort days by dates
    data['days'] = sorted(data['days'], key = lambda x: parse(x["date"]))
    
    # sort events within days by time
    for day in data['days']:
        if len(day['events']) > 1:
            day['events'] = sorted(day['events'], 
                                   key = lambda x: parse(x["time"]))
    
    data['days'][0]['day'] = 1; 
    # if only 1 date, set day and return. else calculate difference
    if len(data['days']) == 0:
        return data
    
    # calculate days by day-differences useing datetime objects via parse
    day0 = data['days'][0]
    for day1 in data['days'][1:]:
        # get datetime objects starting at midnight
        date0 = parse(day0['raw']).replace(hour=0,minute=0)
        date1 = parse(day1['raw']).replace(hour=0,minute=0)
        # get difference in number of days
        day_difference = date1-date0
        day_difference = day_difference.days
        # update 2nd date
        day1['day'] = day0['day'] + day_difference
        # update 1st element for loop
        day0=day1

    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default=None, help="if set, will save to this file. currently only support yaml.")
    parser.add_argument("-s", "--start", default=None, help="start time. format: month/day/year hour:minute, e.g. 5/20/2018 5:34. If nothing set, will use current time.")
    parser.add_argument("-e", "--end", default=None, help="end time. format: month/day/year hour:minute, e.g. 5/20/2018 5:34. If nothing set, will use end of current day.")
    parser.add_argument("-t", "--timezone", default="US/Pacific")
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("-r", "--raw", action='store_true', help="show raw timestamps")
    args = parser.parse_args()


    service = setup_calendar()
    calendar_list = load_calendars_from_file()
    calendars = get_calendars_info(service, calendar_list)

    tzinfo = tz.gettz(args.timezone)
    start, end = load_start_end(args.start, args.end, tzinfo)
    all_events = load_events(service, calendars, start, end, tzinfo)

    if args.verbose or not args.file: 
        # display_events(calendars, all_events, start, end, tzinfo, args.raw)
        print("Printing all events between:")
        print("    %s -> %s " % (start, end))
        sorted_events = flatten_events(all_events, sort=True)
        # import ipdb; ipdb.set_trace()
        apply_to_events(sorted_events, display_event, tzinfo)
    if args.file:
        data = create_events_object(calendars, all_events, start, tzinfo)
        file = open(args.file, 'w')
        yaml.dump(data, file)

if __name__ == "__main__":
    main()


