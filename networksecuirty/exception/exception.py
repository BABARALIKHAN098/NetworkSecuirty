import sys
from networksecuirty.logging import logger


class NetworkSecurityException(Exception):
    """Custom exception that records the file name and line number of the error."""

    def __init__(self, message, error_details: sys):
        # Let the base Exception store the message as usual
        super().__init__(message)
        self.error_message = message

        # exc_info() returns (exception type, exception value, traceback).
        # We only need the traceback, so the first two are ignored.
        _, _, exc_tb = error_details.exc_info()

        # Line number where the error happened
        self.lineno = exc_tb.tb_lineno

        # Name of the file where the error happened
        self.file_name = exc_tb.tb_frame.f_code.co_filename

    def __str__(self):
        # Build a readable message with file name, line number and error text
        return "Error occurred in python script name [{0}] line number [{1}] error message [{2}]".format(
            self.file_name, self.lineno, str(self.error_message)
        )


if __name__ == "__main__":
    try:
        # Write a message to the log file
        logger.logging.info("enter the block")

        # This line raises ZeroDivisionError on purpose, to test the exception
        a = 1 / 0
        print("This will not be printed", a)

    except Exception as e:
        # Wrap the original error in the custom exception
        raise NetworkSecurityException(e, sys)