class ModbusError(Exception):
    """Exception raised when the modbus slave returns an error"""

    def __init__(self, exception_code, value=""):
        """constructor: set the exception code returned by the slave"""
        if not value:
            value = "Modbus Error: Exception code = %d" % (exception_code)
        Exception.__init__(self, value)
        self._exception_code = exception_code

    def get_exception_code(self):
        """return the exception code returned by the slave (see defines)"""
        return self._exception_code

class InvalidArgumentError(Exception):
    """
    Exception raised when one argument of a function doesn't meet
    what is expected
    """
    pass


class ModbusInvalidResponseError(Exception):
    """
    Exception raised when the response sent by the slave doesn't fit
    with the expected format
    """
    pass


class ModbusInvalidRequestError(Exception):
    """
    Exception raised when the request by the master doesn't fit
    with the expected format
    """
    pass


class OutOfModbusBlockError(Exception):
    """Exception raised when accessing out of a modbus block"""
    pass


class MissingKeyError(Exception):
    """
    Exception raised when trying to get an object with a key that doesn't exist
    """
    pass


class DuplicatedKeyError(Exception):
    """
    Exception raised when trying to add an object with a key that is already
    used for another object
    """
    pass


class InvalidModbusBlockError(Exception):
    """Exception raised when a modbus block is not valid"""
    pass


class OverlapModbusBlockError(Exception):
    """
    Exception raised when adding modbus block on a memory address
    range already in use
    """
    pass