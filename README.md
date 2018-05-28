## Goal
I've wanted to template my calendars for years. I think each week is different, but I think weeks repeat. I like to schedule most of my time (even if I don't follow the schedule so strictly) so that I have a foundation to work from. These scripts are my attempt at doing so. The idea right now is to implement 4 functions
* read: this will read calendar events between in a time-frame (and optionally save them) 
* clear: this will clear calendar events in a time-frame
* put: this will put events into the calendar from a file
* move: this will move events within a time-frame "up" or "down"

Together, I should be able to create, save, load, and move events with these scripts. And I think this will facilitate maintaining and editing templates.

## Workflow
You want create and experiment with multiple calendar templates to see which is best. For each one:
  1. Create a template for a week (or some time-length)
  1. Clear across dates that you want to apply this template (from appropriate calendars)
  1. Place from template across those dates
  1. run time-availability script to see buffer


## Getting Started
* Follow [these steps](https://developers.google.com/calendar/quickstart/python) to 
  * turn on the Google Calendar API for this app and 
  * get credentials which will allow this app to interface with the Google Calendar API


## Todo

### Main Functions
1. **Function: read.py**.
   * ~~read in all the calendar events between a set start and end time~~
   * ~~option to save to yaml file~~

2. **Function: clear.py**. 
   * ~~Clear all the calendar events between a set start and end time~~
   * remove a single event or set of events in a time-range by the event name(s)

3. **Function: put.py**. 
   * ~~Using a yaml file, set events for a given day~~
      * ~~set events for multiple days (e.g. 2 days of worth of events)~~
      * ~~repeat both `>=1` (e.g. 1 or 2) days worth of events every `d` days `n` times~~

4. **Function: move.py**. 
   * Pick calendar(s) and event time-frame and move all events in time-frame up/down by x time (days or hours + minutes or both?)
   * filter for things you don't want to be moved
   * can also move all events starting at event named "x" on day y up. for multiple events of same day, can but `-n` option for which one. e.g from `-e block -n 2` would be block 2.

5. **Function: replace.py**.
   * replace the contents within a date-range with a template (potentially tiled)

6. **Function: required_time.py**
   * calculates how much time you need for tasks in a task list defined by a yaml file

7. **Function: available_time.py**
   * Calculate some information on whether you have enough time for your tasks, and by how much if so (i.e. your buffer).

8. **Function: replicate.py**
   * saves a time-span, tiles across a choice of dates, and calculates how well time goes for required tasks. Based on above workflow.

### Other
1. A system of templates, their descriptions/notes with potential to add photos. This auto-populate PDF (or something).
1. Default settings yaml file (for things like timezone)
1. common command-line args across files.
   a. can input calendars from command line (currently just settings file)
<!-- 1. Function that clears previous authorization and redoes authorization -->

## Resources
1. [Google Calendar API](https://developers.google.com/calendar/)