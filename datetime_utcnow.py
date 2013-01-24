#!/usr/bin/env python
# encoding: utf-8
"""
datetime_utcnow.py

Created by donb on 2013-01-24.
Copyright (c) 2013 __MyCompanyName__. All rights reserved.
"""

import sys
import os

import commands
import datetime

# formatting assist

def pr(l,v=None):
    """prints str() of v"""
    if v is not None:
        print "%s:\n\n    %s\n" % (l, v)
    else:
        print "%s\n%s\n" % (l, "_"*len(l))

def prr(l,v=None):
    """prints repr() of v"""
    if v is not None:
        print "%s:\n\n    %r\n" % (l, v)
    else:
        print "%s\n%s\n" % (l, "_"*len(l))


#
#   UNIX command 'date'
#

if False:
    pr("UNIX command 'date'")

    cmd = 'date'

    r = commands.getoutput(cmd)

    pr("UNIX date command", r)

    pr("r.split()[4]", r.split()[4])

#
#   Python datetime
#

if False:
    pr("Python datetime")


    pr('datetime.datetime.now() ', datetime.datetime.now() )
    t =  datetime.datetime.now()  - datetime.datetime.utcnow()

    pr("datetime.now()  - datetime.utcnow()", t)

    pr("timedelta(-1, 68399, 999998) == timedelta(-1, 68400, 0)",
    datetime.timedelta(-1, 68399, 999998) == datetime.timedelta(-1, 68400, 0)
    )

    pr("datetime.timedelta(hours=-5, seconds = -1) < t < datetime.timedelta(hours=-5, seconds = 1)", 
            datetime.timedelta(hours=-5, seconds = -1) < t < datetime.timedelta(hours=-5, seconds = 1))

    # print datetime.timedelta(hours=-5, seconds = 0) < t < datetime.timedelta(hours=-5, seconds = 1)  #False
    # print datetime.timedelta(hours=-5, seconds = -1) < t < datetime.timedelta(hours=-5, seconds = 0)  #True

    t2 = datetime.datetime.utcnow() + t

    pr('strftime("%a %Y.%m.%d %I:%M:%S")',  t2.strftime("%a %Y.%m.%d %I:%M:%S") )

    d3 =         datetime.datetime(2011, 7, 29, 23, 46, 39)


    pr( 'str(d3)', str(d3) )

    prr("_DATETIME_to_python(d3)", _DATETIME_to_python(d3))

def _DATETIME_to_python( in_date ):
    """
    Returns DATETIME column type as datetime.datetime type.
    """
    # pv = None
    # try:

    v = str(in_date) 
    a = v.split(" ")
    fs = 0
    dt = [ int(v) for v in  a[0].split('-') ] +\
         [ int(v) for v in  a[1].split(":") ] + [fs,]
    pv = datetime.datetime(*dt)

    # except ValueError:
    #     pv = None
    
    return pv





#
#   Cocoa (Foundation) NSDate, NSCalendar, NSDateFormatter, etc.
#


pr("Cocoa (Foundation) NSDate, etc.")


from Foundation import NSCalendar, NSDayCalendarUnit, NSWeekdayCalendarUnit,\
    NSYearCalendarUnit,  NSMonthCalendarUnit, NSHourCalendarUnit, \
    NSMinuteCalendarUnit,   NSSecondCalendarUnit, NSTimeZone, NSDate, \
    NSDateFormatter, NSGregorianCalendar, NSLocale
    

date1 = NSDate.dateWithTimeIntervalSinceReferenceDate_(333675999.713839)

date2 = NSDate.dateWithTimeIntervalSinceReferenceDate_(333675999.713839 - 6 * 30 * 24 *60 * 60)


    
pr( "date1" , date1)
pr( "date1" , date2)

prr("_DATETIME_to_python(date1)", _DATETIME_to_python(date1))

# pr( "str(date1) ", str(date1) )


currentCalendar = NSCalendar.currentCalendar()

#
#   time zones
#

def pr_tz(l, tz):
    s = tz.secondsFromGMT() / (60 * 60)
    print "%s:\n\n    %r (%s) offset %d hours%s\n" % (l,tz.name(), tz.abbreviation(), s ,
                    " (**local**)" if  "Local Time Zone " in tz.description() else "") 
    # print tz.description()


timeZone_Current = currentCalendar.timeZone()

timeZone_Local = NSTimeZone.localTimeZone()

timeZone_GMT = NSTimeZone.timeZoneForSecondsFromGMT_(0)

# don't want to really call this "EST" because it is more accurately just GMT-5

timeZone_GMT5 = NSTimeZone.timeZoneForSecondsFromGMT_(-18000)


pr_tz('timeZone_Current', timeZone_Current)

# s = timeZone_Local.secondsFromGMT() / (60 * 60)
# pr("timeZone_Local", str(timeZone_Local) + " offset: %d hours" % s )
# 

pr_tz('timeZone_Local', timeZone_Local)

# s = timeZone_GMT.secondsFromGMT() / (60 * 60)
# pr("timeZone_GMT", str(timeZone_GMT) + " offset: %d hours" % s )
pr_tz('timeZone_GMT', timeZone_GMT)

# s = timeZone_GMT5.secondsFromGMT() / (60 * 60)
# pr("timeZone_GMT5", str(timeZone_GMT5) + " offset: %d hours" % s )
pr_tz('timeZone_GMT5', timeZone_GMT5)

# pr( "timeZone_Local.isDaylightSavingTime()", timeZone_Local.isDaylightSavingTime() ) #  determines whether daylight saving time is currently in effect.
# pr( "timeZone_Local.daylightSavingTimeOffset()", timeZone_Local.daylightSavingTimeOffset() ) # determines the current daylight saving time offset. For most time zones this is either zero or one.
# pr( "timeZone_Local.nextDaylightSavingTimeTransition()", timeZone_Local.nextDaylightSavingTimeTransition())


# pr("timeZone_Local.secondsFromGMT()", timeZone_Local.secondsFromGMT())

#
#       dateFormatter
#

# Formatting for Machines: Controlled Environment Needed
# 
# It is a whole other matter if you need to create a date string according to
# the specification of a certain file format or API.
# In such a case, you usually have to follow a very strict spec to
# make sure the other party can read the string you are generating.

 # By default, NSDateFormatter uses the user’s current calendar and time zone,
 # which are possibly different from the requirements.
 # Most file formats and web APIs use the western, Gregorian calendar,
 # so we need to make sure that our date formatter uses it, too.

dateFormatter = NSDateFormatter.alloc().init()
dateFormatter_Current = NSDateFormatter.alloc().init()
dateFormatter_GMT = NSDateFormatter.alloc().init()


#   format string (formatter)

# format_string = "E yyyy'-'MM'-'dd' 'HH':'mm':'ss VVVV"   # ==> "AD 2011-07-29 19:46:39 United States (New York)"
# format_string = "E yyyy'-'MM'-'dd' 'HH':'mm':'ss VVV"   # ==> " 'Fri 2011-07-29 19:46:39 GMT-04:00'

format_string = "E yyyy'-'MM'-'dd' 'HH':'mm':'ss z"   # ==> 'Fri 2011-07-29 19:46:39 EDT') or 'EST', or 'GMT-04:00'

dateFormatter.setDateFormat_(format_string)
dateFormatter_Current.setDateFormat_(format_string)
dateFormatter_GMT.setDateFormat_(format_string)


pr( "dateFormatter.stringFromDate_(date1)", dateFormatter.stringFromDate_(date1)    )
pr( "dateFormatter.stringFromDate_(date2)", dateFormatter.stringFromDate_(date2)    )

# "timeZoneForSecondsFromGMT"


# locale

locale = NSLocale.alloc().initWithLocaleIdentifier_("en_US_POSIX")

dateFormatter.setLocale_(locale)
dateFormatter_Current.setLocale_(locale)
dateFormatter_GMT.setLocale_(locale)

#   time zone (formatter)

dateFormatter.setTimeZone_(timeZone_Local)
dateFormatter_Current.setTimeZone_(timeZone_Current)
dateFormatter_GMT.setTimeZone_(timeZone_GMT)


pr('dateFormatter.timeZone()', dateFormatter.timeZone())
pr('dateFormatter_Current.timeZone()', dateFormatter_Current.timeZone())
pr('dateFormatter_GMT.timeZone()', dateFormatter_GMT.timeZone())


gregorianCalendar = NSCalendar.alloc().initWithCalendarIdentifier_(NSGregorianCalendar)

# 
pr('gregorianCalendar.timeZone()', gregorianCalendar.timeZone())

dateFormatter.setCalendar_(gregorianCalendar)
dateFormatter_Current.setCalendar_(gregorianCalendar)


pr( "dateFormatter.stringFromDate (2)", dateFormatter_Current.stringFromDate_(date1)    )


myDateString = dateFormatter.stringFromDate_(date1)

pr( "dateFormatter.stringFromDate (1)", myDateString    )

# 2011-07-02 17:02:54 EDT



dateFormatter.setTimeZone_(timeZone_Local)

pr( "dateFormatter.stringFromDate (local time zone)", dateFormatter.stringFromDate_(date1)    )



# print dir(timeZone_GMT)


pr('dateFormatter.timeZone()', dateFormatter.timeZone())
pr('dateFormatter.timeZone()', dateFormatter_Current.timeZone())



print ( "dateFormatter.stringFromDate (GMT)", dateFormatter.stringFromDate_(date1) )
print ( "dateFormatter.stringFromDate (GMT)", dateFormatter.stringFromDate_(date2) )

print ( "dateFormatter.stringFromDate (EST)", dateFormatter_Current.stringFromDate_(date1) )
print ( "dateFormatter.stringFromDate (EST)", dateFormatter_Current.stringFromDate_(date2) )

print ( "dateFormatter.stringFromDate (EST)", dateFormatter_GMT.stringFromDate_(date1) )
print ( "dateFormatter.stringFromDate (EST)", dateFormatter_GMT.stringFromDate_(date2) )


#
# date1_components
#



fcdc = currentCalendar.components_fromDate_(

        NSYearCalendarUnit      |   
        NSMonthCalendarUnit     |  
        NSDayCalendarUnit       | 
        NSHourCalendarUnit      | 
        NSMinuteCalendarUnit    |    
        NSSecondCalendarUnit    ,
        date1 
        
        )

pr(  "currentCalendar.components_fromDate",  
    [ fcdc.year(), fcdc.month(), fcdc.day(), fcdc.hour(), fcdc.minute(), fcdc.second(),  ]
    )


dateOfKeynote = currentCalendar.dateFromComponents_(fcdc)

pr(  "currentCalendar.dateFromComponents", dateOfKeynote )





# pacificTime = NSTimeZone.timeZoneWithName_("America/Miami")
# 
# currentCalendar.setTimeZone_(pacificTime)
