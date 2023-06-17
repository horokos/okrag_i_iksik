import os
import sys
import time
import atexit
import select
import logging
import logging.handlers
from signal import SIGTERM


class ServerLogger():
    """Class providing logging to syslog"""
    def __init__(self, loglevel=logging.DEBUG):
        self.my_logger = logging.getLogger('MyLogger')
        self.my_logger.setLevel(loglevel)
        handler = logging.handlers.SysLogHandler(address = '/dev/log')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.my_logger.addHandler(handler)
    
    def setlog(self, loglevel):
        if loglevel == 1:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO
        self.my_logger.setLevel(loglevel)

    def info(self, message):
        self.my_logger.info(message)
    
    def warning(self, message):
        self.my_logger.warning(message)
    
    def error(self, message):
        self.my_logger.error(message)
    
    def critical(self, message):
        self.my_logger.critical(message)
    
    def debug(self, message):
        self.my_logger.debug(message)


class Daemon:
    """A daemon class. Usage: subclass the Daemon class and override the run() method"""
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.log = ServerLogger()
    
    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('Fork1 error: {0}\n'.format(err))
            sys.exit(1)
        os.chdir('/')
        os.setsid()
        os.umask(0)
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write('Fork2 error: {0}\n'.format(err))
            sys.exit(1)
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'w')
        se = open(os.devnull, 'w')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        #file pid
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile,'w+').write("%s\n" % pid)
    
    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon"""
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "Pidfile {0} already exist. Daemon already running?\n".format(self.pidfile)
            sys.stderr.write(message)
            sys.exit(1)
        # Start the daemon
        self.daemonize()
        self.log.info("Started daemon")
        self.run()

    def stop(self):
        """Stop the daemon"""
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if not pid:
            message = "Pidfile {0} does not exist. Daemon not running?\n".format(self.pidfile)
            sys.stderr.write(message)
            return
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
                self.log.info("Stopped daemon")
        except:
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
            else:
                sys.exit(1)
    
    def status(self):
        """Check daemon status"""
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if pid:
            message = "● serwer - Kolko i krzyzyk serwer daemon\nActive: active (running)\nMain PID: {0} (serwer)\n".format(pid)
            sys.stdout.write(message)
            sys.exit(0)
        else:
            message = "○ server - Kolko i krzyzyk serwer daemon\nActive: inactive (stopped)\nMain Pidfile: {0} (serwer)\n".format(self.pidfile)
            sys.stdout.write(message)
            sys.exit(0)

    def restart(self):
        """Restart the daemon"""
        self.log.info("Restarting server")
        self.stop()
        self.start()

    def run(self):
        #will be overwritten
        pass
