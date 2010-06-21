# -*- coding: utf-8 -*-
"""Provides managed logging."""

from static import LOGLEVEL

from sys import version_info, stdout
from datetime import datetime

#TODO: make 'extra' work properly

class MythLog( LOGLEVEL ):
    """
    MythLog(module='pythonbindings', lstr=None, lbit=None, \
                    db=None) -> logging object

    'module' defines the source of the message in the logs
    'lstr' and 'lbit' define the message filter
        'lbit' takes a bitwise value
        'lstr' takes a string in the normal '-v level' form
        default is set to 'important,general'

    The filter level is global values, shared between all logging instances.
    The logging object is callable, and implements the MythLog.log() method.
    """

    LEVEL = LOGLEVEL.IMPORTANT|LOGLEVEL.GENERAL
    LOGFILE = stdout

    helptext = """Verbose debug levels.
 Accepts any combination (separated by comma) of:

 "  all          "  -  ALL available debug output 
 "  most         "  -  Most debug (nodatabase,notimestamp,noextra) 
 "  important    "  -  Errors or other very important messages 
 "  general      "  -  General info 
 "  record       "  -  Recording related messages 
 "  playback     "  -  Playback related messages 
 "  channel      "  -  Channel related messages 
 "  osd          "  -  On-Screen Display related messages 
 "  file         "  -  File and AutoExpire related messages 
 "  schedule     "  -  Scheduling related messages 
 "  network      "  -  Network protocol related messages 
 "  commflag     "  -  Commercial detection related messages
 "  audio        "  -  Audio related messages 
 "  libav        "  -  Enables libav debugging 
 "  jobqueue     "  -  JobQueue related messages 
 "  siparser     "  -  Siparser related messages 
 "  eit          "  -  EIT related messages 
 "  vbi          "  -  VBI related messages 
 "  database     "  -  Display all SQL commands executed 
 "  dsmcc        "  -  DSMCC carousel related messages 
 "  mheg         "  -  MHEG debugging messages 
 "  upnp         "  -  upnp debugging messages 
 "  socket       "  -  socket debugging messages 
 "  xmltv        "  -  xmltv output and related messages 
 "  dvbcam       "  -  DVB CAM debugging messages 
 "  media        "  -  Media Manager debugging messages 
 "  idle         "  -  System idle messages 
 "  channelscan  "  -  Channel Scanning messages 
 "  extra        "  -  More detailed messages in selected levels 
 "  timestamp    "  -  Conditional data driven messages 
 "  none         "  -  NO debug output 
 
 The default for this program appears to be: '-v  "important,general" '

 Most options are additive except for none, all, and important.
 These three are semi-exclusive and take precedence over any
 prior options given.  You can however use something like
 '-v none,jobqueue' to get only JobQueue related messages
 and override the default verbosity level.
 
 The additive options may also be subtracted from 'all' by 
 prefixing them with 'no', so you may use '-v all,nodatabase'
 to view all but database debug messages.
 
 Some debug levels may not apply to this program.
"""

    def __repr__(self):
        return "<%s '%s','%s' at %s>" % \
                (str(self.__class__).split("'")[1].split(".")[-1], 
                 self.module, bin(self.LEVEL), hex(id(self)))

    def __init__(self, module='pythonbindings', lstr=None, lbit=None, db=None):
        if lstr or lbit:
            self._setlevel(lstr, lbit)
        self.module = module
        self.db = db
        self.time = self._time25
        if version_info >= (2,6): # 2.6 or newer
            self.time = self._time26

    @classmethod
    def _setlevel(cls, lstr=None, lbit=None):
        """Manually set loglevel."""
        if lstr:
            cls.LEVEL = cls._parselevel(lstr)
        elif lbit:
            cls.LEVEL = lbit

    @classmethod
    def _setfile(cls, filename):
        """Redirect log output to a specific file."""
        cls._setfileobject(open(filename, 'w'))

    @classmethod
    def _setfileobject(cls, fileobject, close=True):
        """Redirect log output to an opened file pointer."""
        if (cls.LOGFILE.fileno() != 1) and close:
            cls.LOGFILE.close()
        cls.LOGFILE = fileobject

    @classmethod
    def _parselevel(cls, lstr=None):
        bwlist = (  'important','general','record','playback','channel','osd',
                    'file','schedule','network','commflag','audio','libav',
                    'jobqueue','siparser','eit','vbi','database','dsmcc',
                    'mheg','upnp','socket','xmltv','dvbcam','media','idle',
                    'channelscan','extra','timestamp')
        if lstr:
            level = cls.NONE
            for l in lstr.split(','):
                if l in ('all','most','none'):
                    # set initial bitfield
                    level = eval('MythLog.'+l.upper())
                elif l in bwlist:
                    # update bitfield OR
                    level |= eval('MythLog.'+l.upper())
                elif len(l) > 2:
                    if l[0:2] == 'no':
                        if l[2:] in bwlist:
                            # update bitfield NOT
                            level &= level^eval('MythLog.'+l[2:].upper())
            return level
        else:
            level = []
            for l in xrange(len(bwlist)):
                if cls.LEVEL&2**l:
                    level.append(bwlist[l])
            return ','.join(level)

    def _time25(self): return datetime.now().strftime('%Y-%m-%d %H:%M:%S.000')
    def _time26(self): return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def log(self, level, message, detail=None):
        """
        MythLog.log(level, message, detail=None) -> None

        'level' sets the bitwise log level, to be matched against the log
                    filter. If any bits match true, the message will be logged.
        'message' and 'detail' set the log message content using the format:
                <timestamp> <module>: <message>
                        ---- or ----
                <timestamp> <module>: <message> -- <detail>
        """
        if level&self.LEVEL:
            lstr = "%s %s: %s" % (self.time(), self.module, message)
            if detail is not None:
                lstr += " -- %s" % detail
            self.LOGFILE.write(lstr+'\n')
            self.LOGFILE.flush()
        return

#        if (dblevel is not None) and (self.db is not None):
#            c = self.db.cursor(self.log)
#            c.execute("""INSERT INTO mythlog (module,   priority,   logdate,
#                                              host,     message,    details)
#                                    VALUES   (%s, %s, %s, %s, %s, %s)""",
#                                    (self.module,   dblevel,    now(),
#                                     self.host,     message,    detail))
#            c.close()

    def __call__(self, level, message, detail=None):
        self.log(level, message, detail)
