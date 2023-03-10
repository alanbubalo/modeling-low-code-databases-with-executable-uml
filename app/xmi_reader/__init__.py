"""
Package for generating parts of a UML model.

Get:

- classes
- class names
- data types
- enumerations
- attributes
- associations

"""
from app.xmi_reader.packaged_elements import get_packaged_elements
from app.xmi_reader.classes import get_classes
from app.xmi_reader.data_types import get_data_types, get_enumerations
from app.xmi_reader.attributes import get_attributes
from app.xmi_reader.associations import get_associations, get_class_name

__all__ = [
    'get_packaged_elements',
    'get_classes',
    'get_class_name',
    'get_data_types',
    'get_enumerations',
    'get_attributes',
    'get_associations',
]
