#!/usr/bin/env python3
import os
import sys
import time
import pwd
import atexit
from configparser import ConfigParser
from datetime import datetime



def main():
    if os.getuid():
        print("You need to bee superuser")
        sys.exit(1)
    config = ConfigParser()
    config.read('config.ini')
    user = config.get('DEFAULT', 'user')
    pw = pwd.getpwnam(user)
    uid, gid = pw.pw_uid, pw.pw_gid
    log_output = config.get('DEFAULT', 'log_output')
    log_error  = config.get('DEFAULT', 'log_error')
    pid_file   = config.get('DEFAULT', 'pid_file')



    pid = os.fork()
    if pid:
        sys.exit(0)
    
    # Becomes user from config
    os.setgid(gid)
    os.setuid(uid)

    # Detouch from parent
    os.umask(0)
    os.setsid()
    os.chdir('/')

    # Second fork
    pid = os.fork()
    if pid:
        sys.exit(0)
    
    # Check for double run
    with open(pid_file, 'r') as f:
        if f.readline():
            print('Another copy of script runned')
            sys.exit(1)

    # Redirect all files
    si = open('/dev/null', 'r')
    so = open(log_output, 'a+')
    se = open(log_error, 'ab+', 0) # disable buffering
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    
    # Write pid file
    open(pid_file, 'w+').write('%d\n' % os.getpid())
    def del_pid():
       open(pid_file, 'w+').truncate() 

    atexit.register(del_pid)
    
    # do work
    while True:
        print(datetime.now())
        time.sleep(3)


if __name__ == '__main__':
    main()
