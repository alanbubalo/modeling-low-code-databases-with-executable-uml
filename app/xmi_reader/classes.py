"""Module for generating a dictionary of classes with their associated id."""
from xml.dom.minicompat import NodeList
from xml.dom.minidom import Element


def get_classes(packaged_elements: NodeList[Element]) -> dict[str, Element]:
    """Returns a dictionary of classes with their matching ID based on provided packaged
    elements."""

    return {
        element.getAttribute("xmi:id"): element
        for element in packaged_elements
        if element.getAttribute("xmi:type") == "uml:Class"
    }
