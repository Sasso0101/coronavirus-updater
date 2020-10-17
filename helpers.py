import sys

def checkForce():
    ''' Check if the user has passed the cmd argument force '''
    if len(sys.argv) > 1:
        if sys.argv[1] == 'force':
            return True
        else: return False