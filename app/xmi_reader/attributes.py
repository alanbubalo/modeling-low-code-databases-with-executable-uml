"""Module for generating fields associated by attributes in UML model"""
from xml.dom.minidom import Element
import random

COLORS = (
    "light-blue", "blue", "dark-blue",
    "light-green", "green", "dark-green",
    "light-yellow", "yellow", "dark-yellow",
    "light-red", "red", "dark-red",
    "light-gray", "gray", "dark-gray"
)

DATE_FORMAT = "EU"
TIMEZONE = "Europe/Zagreb"


def get_field(enumerations: list[dict], name: str, type_: str) -> dict:
    """ Create a new field based on the attribute. """
    field = {}
    field["name"] = name.title().replace("_", " ")
    lower_name = type_.lower()

    # Handling Number Type
    if lower_name in ("integer", "int", "unsigned integer",
                      "unsigned int", "float", "real", "double"):
        field["type"] = "number"
        field["number_decimal_places"] = 0
        field["number_negative"] = lower_name not in ("unsigned integer", "unsigned int")
        field["number_decimal_places"] = 5 if lower_name in ("float", "real", "double") else 0

    # Handling Long Text Type
    elif lower_name in ("blob", "long text"):
        field["type"] = "long_text"

    # Handling URL Type
    elif lower_name == "url":
        field["type"] = "url"

    # Handling Email Type
    elif lower_name == "email":
        field["type"] = "email"

    # Handling Rating Type
    elif lower_name == "rating":
        field["type"] = "rating"
        field["max_value"] = 5
        field["color"] = "yellow"
        field["style"] = "star"

    # Handling Boolean Type
    elif lower_name in ("boolean", "bool"):
        field["type"] = "boolean"

    # Handling Date
    elif lower_name == "date":
        field["type"] = "date"
        field["date_format"] = DATE_FORMAT
        field["date_include_time"] = False

    elif lower_name in ("time", "datetime"):
        field["type"] = "date"
        field["date_format"] = DATE_FORMAT
        field["date_include_time"] = True
        field["date_time_format"] = "24"

    # Handling Last Modified Type
    elif lower_name == "last modified":
        field["type"] = "last_modified"
        field["date_format"] = DATE_FORMAT
        field["date_include_time"] = False
        field["date_include_time"] = True
        field["timezone"] = TIMEZONE

    # Handling Created On Type
    elif lower_name == "created on":
        field["type"] = "created_on"
        field["date_format"] = DATE_FORMAT
        field["date_include_time"] = False
        field["date_include_time"] = True
        field["timezone"] = TIMEZONE

    # Handling File Type
    elif lower_name == "file":
        field["type"] = "file"

    # Handling Phone Number Type
    elif lower_name in ("phone", "phone number", "telephone", "telephone number"):
        field["type"] = "phone_number"

    # Handling Multiple_Collaborators Type
    elif lower_name in ("collaborators", "multiple collaborators"):
        field["type"] = "multiple_collaborators"

    # Handling Multiple Select Type
    elif lower_name in (enum["name"].lower() for enum in enumerations):
        exact_enum = next(enum for enum in enumerations if enum["name"] == type_)
        field["type"] = "multiple_select"
        field["select_options"] = [{
            "value": value,
            "color": random.choice(COLORS)
        } for value in exact_enum["literals"]]

    # If a Data Type is not defined or is a string, it's just a text
    else:
        field["type"] = "text"
        # field["text_default"] = ""

    return field


def get_attributes(classes: dict[str, Element],
                   data_types: list[dict],
                   enumerations: list[dict]
) -> dict[str, list]:
    """Generates a dictionary of class attributes for each class.

    Args:
        classes: Dictionary of classes with their ID
        data_types: list of all data types
        enumerations: list of all enumerations

    Returns:
        A dictionary of lists of class attributes for each class identifier
    """

    class_attributes = {_id: [] for _id in classes.keys()}

    for _id, _class in classes.items():
        owned_attributes = _class.getElementsByTagName("ownedAttribute")

        for attribute in owned_attributes:
            found_type = ""
            if attribute.getAttribute("type") != "":
                found_type = next(data_type["name"] for data_type in data_types
                                  if data_type["id"] == attribute.getAttribute("type"))

            class_attributes[_id].append(get_field(
                enumerations, attribute.getAttribute("name"), found_type
            ))

    return class_attributes
