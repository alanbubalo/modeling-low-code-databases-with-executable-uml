"""Module for initializing DOM object of the given XMI file"""
from xml.dom.minidom import parse, Element
from xml.dom.minicompat import NodeList
from app import upload_dir

UPLOAD_DIR = upload_dir['path']

def get_packaged_elements(user_id, xmi_file) -> NodeList[Element]:
    """Get all packaged elements from the XMI file

    Returns:
        All elements in <'uml:Model'> with a tag '<packagedElements'>
    
    Raises:
        KeyError: If XMI_FILE attribute is not specified in the .env file
    """

    if not xmi_file:
        raise KeyError('XMI_FILE attribute is not specified in the .env file')

    file = parse(f"{UPLOAD_DIR}/user-{user_id}/{xmi_file}")
    xmi = file.firstChild
    # doc = xmi.firstChild
    model = xmi.getElementsByTagName("uml:Model")[0]
    return model.getElementsByTagName("packagedElement")
