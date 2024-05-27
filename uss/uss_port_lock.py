'''
Created on Sep 12, 2013

@author: Sven
'''



class lock_state:
    UNLOCKED = 0
    LOCKED = 1
    NOT_CONNECTED = 2
    STATE_UNKNOWN = 3

    state_strings = {
        UNLOCKED: "Unlocked",  # Lock is open / unlocked.
        LOCKED: "Locked",    # Lock is closed / locked.
        NOT_CONNECTED: "Not connected", # No motor / lock is connected.
        STATE_UNKNOWN: "Unknown"
    }


class lock_command:
    # lock commands
    UNLOCK  = 0     # Unlock, returns state of lock.
    LOCK = 1        # Lock, returns state of lock.
    QUERY = 2       # Query state of lock.


class lock(object):

    def __init__(self, port, lock=1):
        self._port = port
        if lock == 2:
            self._lock_func = self._port.lock2_command
        else:
            self._lock_func = self._port.lock1_command
        self._status = lock_state.STATE_UNKNOWN

    def update(self):
        self._status = self._lock_func(lock_command.QUERY)
        return self.__str__()

    def lock(self):
        self._status = self._lock_func(lock_command.LOCK)
        return self.__str__()

    def unlock(self):
        self._status = self._lock_func(lock_command.UNLOCK)
        return self.__str__()

    def get_state(self):
        return self._status

    def __str__(self):
        try:
            return lock_state.state_strings[self._status]
        except KeyError:
            return lock_state.state_strings[self._status]


