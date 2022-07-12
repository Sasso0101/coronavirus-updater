import sys

def isForced():
    ''' Check if the user has passed the cmd argument force '''
    if len(sys.argv) > 1:
        if 'force' in sys.argv:
            return True
        else: return False

def noNotifications():
    ''' Check if the user has passed the cmd argument to avoid sending notifications '''
    if len(sys.argv) > 1:
        if 'noNotifications' in sys.argv:
            return True
        else: return False