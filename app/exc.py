"""
Exceptions used in the application.

"""

class NotFoundException(Exception):
    """
    Exception raised when something (model) is not found

    """

class NotAuthorizedException(Exception):
    """
    Exception raised when client token is incorrect.
    
    """


class InvalidGroupException(Exception):
    """
    Exception raised when group is invalid.
    
    """


class InvalidDatabaseException(Exception):
    """
    Exception raised when database is invalid.
    
    """


class BadFieldException(Exception):
    """
    Exception raised when something goes wrong while creating a new field.
    
    """


class DeletingDatabasesException(Exception):
    """
    Exception raised when something goes wrong while deleting a database.
    
    """


class BadRequestException(Exception):
    """
    Exception raised when Baserow request throws an error.
    
    """
    def __init__(self, json, status_code):            
        # Call the base class constructor with the parameters it needs
        super().__init__("")

        # Now for your custom code...
        self.json = json
        self.status_code = status_code
