"""
    available_time.py by Wilka Carvalho
"""
# python utils
import yaml
from pprint import pprint
import argparse

# date utilities
from dateutil.parser import parse
from dateutil import tz
from datetime import datetime, timedelta

# this library
from lib import get_calendars_info, setup_calendar, load_start_end, load_yaml, flatten_events
from read import load_events


def get_calendars_from_tasks(tasks):
    """See the calendars that will be queried using task data
    """
    calendars = set()
    for task in tasks:
      calendars.add(task['calendar'])
    return list(calendars)


def flatten_tasks(task_data):
  tasks = []
  for category in task_data:
    for task in task_data[category]:
      task['category'] = category
      tasks.append(task)

  return tasks

def calculate_time_availability_by_calendar(events, tasks, end, tzinfo):
  for task in tasks:
    if not 'end' in task: 
      if 'start' in task:
        task['end'] = parse(task['start']).replace(tzinfo=tzinfo)
        task['end'] = task['end'] if task['end'] > end else end
      else:
        task['end'] = end
        # task['end'] = parse(task['end']).replace(tzinfo=tzinfo)

  tasks = sorted(tasks, key = lambda x: x['end'])

  # turn start dateTime into a datetime object for all events
  for event in events:
    event['start']['dateTime'] = parse(event['start']['dateTime'])
  # turn events into an iterable to query
  events = sorted(events, key = lambda x: x['start']['dateTime'])

  nevents = len(events)
  
  def time_until_duedate(duedate, indx):
    time = 0
    while indx < nevents:
      event = events[indx]
      event_start = event['start']['dateTime']
      event_end = parse(event['end']['dateTime'])

      if event_end >= duedate: 
        indx -= 1
        break

      event_length = int((event_end-event_start).total_seconds()/60)
      time += event_length
      indx += 1
    return time, indx

  indx = 0
  calendar_time = 0
  prev_duedate = None
  # completed = []
  # not_completed = []
  for task in tasks:
    duedate = task['end'] + timedelta(days=1) # to include that day in the available time

    # if looking at new duedate, add available time from calendars
    if duedate == prev_duedate:
      time = 0
    else:
      time, indx = time_until_duedate(duedate, indx)
      calendar_time += time

    # get task time in minutes
    task_time = task['time']*60
    if 'repeat' in task: task_time *= int(task['repeat'])
    # subtract time
    calendar_time -= task_time

    # update duedate
    prev_duedate = duedate

    if calendar_time < 0:
      calendar_time += task_time
      print()
      print("There is not enough time to complete %s: %s" % (task['category'], task['name']))
      print("Available time: %d | Task time: %d" %(calendar_time, task_time))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default=None, help="yaml file to load task data from.")
    parser.add_argument("-s", "--start", default=None, help="start time. format: month/day/year hour:minute, e.g. 5/20/2018 5:34. If nothing set, will use current time.")
    parser.add_argument("-e", "--end", default=None, help="end time. format: month/day/year hour:minute, e.g. 5/20/2018 5:34. If nothing set, will use end of current day.")
    parser.add_argument("-t", "--timezone", default="US/Pacific")
    parser.add_argument("-v", "--verbose", action='store_true')
    args = parser.parse_args()

    tzinfo = tz.gettz(args.timezone)

    task_data = load_yaml(args.file)
    tasks = flatten_tasks(task_data)

    service = setup_calendar()
    calendar_names = get_calendars_from_tasks(tasks)
    calendars = get_calendars_info(service, calendar_names)

    start, end = load_start_end(args.start, args.end, tzinfo)
    all_events = load_events(service, calendars, start, end)
    
    # have dict of calendar -> relevant events
    tasks_by_calendar = {cal:[] for cal in calendars}
    for task in tasks:
      tasks_by_calendar[task['calendar']].append(task)

    # calculate if there's enough time in a calendar for the tasks of that calendar
    for calendar in calendars:
      calculate_time_availability_by_calendar(all_events[calendar], tasks_by_calendar[calendar], end, tzinfo)


if __name__ == '__main__':
  main()