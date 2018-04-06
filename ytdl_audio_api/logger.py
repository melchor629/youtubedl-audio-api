"""
In-memory logger for capture the logs and access
them after.
"""
import io


class InMemoryLogger(object):
    """
    Logger that stores every logged message in memory
    """
    def __init__(self):
        self.__stream = io.StringIO()

    def debug(self, msg):
        """ Debug log """
        self.__stream.write(msg)
        self.__stream.write('\n')

    def warning(self, msg):
        """ Warning log """
        self.debug(msg)

    def error(self, msg):
        """ Error log """
        self.__stream.write('[error] ')
        self.debug(msg)

    def get(self):
        """ Gets the stored logs as str """
        return self.__stream.getvalue()

    def clear(self):
        """ Clears the memory buffer """
        self.__stream = io.StringIO()
