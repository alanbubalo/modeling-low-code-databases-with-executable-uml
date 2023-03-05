"""
### Error class

A proper error class according to Microsoft REST API Guidelines for displaying error \
information. It's currently not used because some errors are automatically formatted like this:

```json
{
    "msg": "Message example."
}
```

https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md#7102-error-condition-responses
"""
class Error():
    """Error"""
    code: str
    message: str

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __dict__(self):
        return {
            "error": {
                "code": self.code,
                "message": self.message
            }
        }
