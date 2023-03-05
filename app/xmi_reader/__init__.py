"""Package for generating parts of the model"""
from app.xmi_reader.packaged_elements import get_packaged_elements
from app.xmi_reader.classes import get_classes
from app.xmi_reader.data_types import get_data_types, get_enumerations
from app.xmi_reader.attributes import get_attributes
from app.xmi_reader.associations import get_associations

# Test
if __name__  == '__main__':
    packaged_elements = get_packaged_elements(1, 'new_hello')
    classes = get_classes(packaged_elements)
    data_types = get_data_types(packaged_elements)
    enumerations = get_enumerations(packaged_elements)
    associations = get_associations(classes)
    attributes = get_attributes(classes, data_types, enumerations)

    print(f"{packaged_elements = }")
    print(f"{classes = }")
    print(f"{data_types = }")
    print(f"{enumerations = }")
    print(f"{associations = }")
    print(f"{attributes = }")
