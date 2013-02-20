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


#   see dates module for list of timezones and formatters


from Foundation import NSCalendar, NSDayCalendarUnit, NSWeekdayCalendarUnit,\
    NSYearCalendarUnit,  NSMonthCalendarUnit, NSHourCalendarUnit, \
    NSMinuteCalendarUnit,   NSSecondCalendarUnit, NSTimeZone, NSDate, \
    NSDateFormatter, NSGregorianCalendar, NSLocale

# choose some timezones with which to display some dates, they're fun!
    
time_zones = [
    ('Local' , NSTimeZone.localTimeZone()) ,
    ('GMT' ,   NSTimeZone.timeZoneForSecondsFromGMT_(0))
    # ('G' , NSTimeZone.timeZoneWithAbbreviation_(u'GMT'))
]

dateFormatters = [ {'name' : n , 'tz' : tz, 'df' : NSDateFormatter.alloc().init() } for n, tz in time_zones ]
map ( lambda y : NSDateFormatter.setTimeZone_(y[0], y[1])  , [ (x['df'], x['tz']) for x in dateFormatters] )

format_string = "E yyyy'-'MM'-'dd' 'HH':'mm':'ss z" # ==> 'Fri 2011-07-29 19:46:39 EDT' or 'EST', or 'GMT-04:00'
format_string = "E yyyy.MM.dd HH:mm z"              # ==> Tue 2012.04.03 00:39 EDT

map ( lambda y : NSDateFormatter.setDateFormat_(y, format_string)  , [x['df'] for x in dateFormatters] )

def print_timezones(l):
        print l + ":" # "time_zones:"
        print
        s = [   "%12s: %s" % (x['name'], "%r (%s) %s%s" % tz_pr(x['tz']) ) for x in dateFormatters ]
        print "\n".join(s)
        print

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

def tz_pr(tz):
    return (
            tz.name(),
            tz.abbreviation(),
            "offset %d hours" % (tz.secondsFromGMT() / (60 * 60) ),
            "(**local**)" if  "Local Time Zone " in tz.description() else ""
            )

    
currentCalendar = NSCalendar.currentCalendar()
    

def get_datestrings(dx, date1):
    return map ( lambda y : (y[0], NSDateFormatter.stringFromDate_(y[1], date1))  , [ (x['name'] , x['df']) for x in dx] )

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

def main():
    
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






    #
    #   Cocoa (Foundation) NSDate, NSCalendar, NSDateFormatter, etc.
    #


    pr("Cocoa (Foundation) NSDate, etc.")




    date1 = NSDate.dateWithTimeIntervalSinceReferenceDate_(333675999.713839)

    date2 = NSDate.dateWithTimeIntervalSinceReferenceDate_(333675999.713839 - 6 * 30 * 24 *60 * 60)

    date3 = NSDate.dateWithTimeIntervalSinceNow_(0)

    pr( "date1" , date1)
    pr( "date2" , date2)
    pr( "date3" , date3)

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


    # timeZone_Current = currentCalendar.timeZone()
    #
    # pr_tz('timeZone_Local', timeZone_Local)
    #
    # # s = timeZone_GMT.secondsFromGMT() / (60 * 60)
    # # pr("timeZone_GMT", str(timeZone_GMT) + " offset: %d hours" % s )
    # pr( "timeZone_Local.isDaylightSavingTime()", timeZone_Local.isDaylightSavingTime() ) #  determines whether daylight saving time is currently in effect.
    # pr( "timeZone_Local.daylightSavingTimeOffset()", timeZone_Local.daylightSavingTimeOffset() ) # determines the current daylight saving time offset. For most time zones this is either zero or one.
    # pr( "timeZone_Local.nextDaylightSavingTimeTransition()", timeZone_Local.nextDaylightSavingTimeTransition())

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

    dateFormatter_Local           = NSDateFormatter.alloc().init()
    dateFormatter_Current   = NSDateFormatter.alloc().init()
    dateFormatter_GMT       = NSDateFormatter.alloc().init()
    dateFormatter_GMT5      = NSDateFormatter.alloc().init()
    dateFormatter_NY      = NSDateFormatter.alloc().init()

    # dateFormatter_Local.__name__ = 'dateFormatter_Local'


    formatter_names = [   ]

    time_zones = [
    
        ('Local' , NSTimeZone.localTimeZone()) ,
    
        ('Current' , currentCalendar.timeZone()) ,
    
        ('GMT' ,   NSTimeZone.timeZoneForSecondsFromGMT_(0)) ,
    
        ('GMT5' , NSTimeZone.timeZoneForSecondsFromGMT_(-18000)) ,
    
        ('NY' , NSTimeZone.timeZoneWithName_(u'America/New_York')) ,
    
        ('System', NSTimeZone. systemTimeZone() ) ,
    
        ('G' , NSTimeZone.timeZoneWithAbbreviation_(u'GMT'))

    ]

    dx = [ {'name' : n , 'tz' : tz, 'df' : NSDateFormatter.alloc().init() } for n, tz in time_zones ]

    

    s = [   "%12s: %s" % (x['name'], "%r (%s) %s%s" % tz_pr(x['tz']) ) for x in dx ]
    print "\n".join(s)
    print

    

    def eq_classes(dx, k):
    
        # z = []
        d = {}
        for n, x in enumerate(dx):
            if x[k] not in d:        
                d[x[k]] = set([ x['name'] ])        
            for m in range(n):
                y = dx[m]
                if x != y and x[k] == y[k]:
                    # z.append((x['name'], y['name']))
                    if x[k] in d:
                        d[x[k]].add( x['name'] )
                    # else:
                    #     d[x[k]] = set([ x['name'] ])
                
                    if y[k] in d:
                        d[y[k]].add( y['name'] )
                    # else:
                    #     d[y[k]] = [ y['name'] ]
    
        return d


    print "eq_classes of dx (under tz):"
    print

    eq_classes_dx = eq_classes(dx, 'tz')

    print "\n".join([ "%20s: %s" % (x.name(), list(eq_classes_dx[x])) for x in eq_classes_dx])
    print


    eq_names =  [ list(eq_classes_dx[x])[0] for x in eq_classes_dx ]
    dx =  [ z for z in dx if z['name'] in eq_names ]


    s = [   "%12s: %s" % (x['name'], "%r (%s) %s%s" % tz_pr(x['tz']) ) for x in dx ]
    print "\n".join(s)
    print


    # print "\n".join([ "%20s: %r" % [k for k in x]  for x in dx ])

    #   format string (formatter)

    # format_string = "E yyyy'-'MM'-'dd' 'HH':'mm':'ss VVVV"   # ==> "AD 2011-07-29 19:46:39 United States (New York)"
    # format_string = "E yyyy'-'MM'-'dd' 'HH':'mm':'ss VVV"   # ==> " 'Fri 2011-07-29 19:46:39 GMT-04:00'

    format_string = "E yyyy'-'MM'-'dd' 'HH':'mm':'ss z"   # ==> 'Fri 2011-07-29 19:46:39 EDT') or 'EST', or 'GMT-04:00'

    map ( lambda y : NSDateFormatter.setDateFormat_(y, format_string)  , [x['df'] for x in dx] )


    # locale

    locale = NSLocale.alloc().initWithLocaleIdentifier_("en_US_POSIX")

    pr("NSDate.date()", NSDate.date())


    map ( lambda y : NSDateFormatter.setLocale_(y, locale)  , [x['df'] for x in dx] )

    map ( lambda y : NSDateFormatter.setTimeZone_(y[0], y[1])  , [ (x['df'], x['tz']) for x in dx] )

    pr('descriptionWithCalendarFormat:timeZone:locale', 
            date1.descriptionWithCalendarFormat_timeZone_locale_( None, None, locale) )
            #         format_string,NSTimeZone.timeZoneForSecondsFromGMT_(-18000),locale

    pr('descriptionWithCalendarFormat:timeZone:locale', 
            date1.descriptionWithCalendarFormat_timeZone_locale_( None, NSTimeZone.timeZoneForSecondsFromGMT_(-18000), locale) )
            #         format_string,NSTimeZone.timeZoneForSecondsFromGMT_(-18000),locale

        
    for a in [date1, date2, date3]:
        dsd = get_datestrings(dx, a)

        s = [   "%12s: %r" % (x[0], x[1] ) for x in dsd ]
        print "\n".join(s)
        print
    
    


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



if __name__ == "__main__":
        main()
        