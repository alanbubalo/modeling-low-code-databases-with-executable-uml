"""Module for generating enumerations and data types."""
from xml.dom.minicompat import NodeList
from xml.dom.minidom import Element


def get_enumerations(packaged_elements: NodeList[Element]) -> list[dict]:
    """Generates a list of all enumerations used in a model.

    Every dictionary in a list represents a single enumeration and contains:
        id (`str`): class identifier
        name (`str`): enumeration name
        literals (`set`): all literals in the enumeration

    Examples:
        >>> enumerations[0]
        {'id': 'AAAAAAGD1hiG1uaORTo=', 'name': 'Gender', 'literals': {'Male', 'Female'}}

    Args:
        packaged_elements: Elements from `<uml:Model` with a tag
            `<packagedElement>`

    Returns:
        A list of all enumerations used in a model
    """

    enumerations = (element for element in packaged_elements
                    if element.getAttribute("xmi:type") == "uml:Enumeration")

    return [{
        "id": enum.getAttribute("xmi:id"),
        "name": enum.getAttribute("name"),
        "literals": {
            literal.getAttribute("name")
            for literal in enum.getElementsByTagName("ownedLiteral")
        }
    } for enum in enumerations]


def get_data_types(packaged_elements: NodeList[Element]) -> list[dict]:
    """Generates a list of all data types used in a model.

    Every dictionary in a list represents a single enumeration and contains:
        id (`str`): data type identifier
        name (`str`): data type name
    
    Examples:
        >>> get_data_types(packaged_elements)[0]
        {'id': 'AAAAAAGD1hiG1uaORTo=', 'name': 'Integer'}

    Args:
        packaged_elements: Elements from `<uml:Mode'> with a tag
            '<packagedElement>`

    Returns:
        A list of all data types used in a model
    """

    data_types = (element for element in packaged_elements
                          if element.getAttribute("xmi:type") == "uml:DataType")

    return [{
        "id":  data_type.getAttribute("xmi:id"),
        "name" : data_type.getAttribute("name")
    } for data_type in data_types]
