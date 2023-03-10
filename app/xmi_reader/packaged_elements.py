"""Module for initializing DOM object of the given XMI file"""
from xml.dom.minidom import parse, Element
from xml.dom.minicompat import NodeList
from app import upload_dir

UPLOAD_DIR = upload_dir['path']

def get_packaged_elements(user_id: int, xmi_file: str) -> NodeList[Element]:
    """Get all packaged elements from the XMI file

    Returns:
        All elements in <'uml:Model'> with a tag '<packagedElements'>
    
    Raises:
        KeyError: If XMI file is not specified
    """

    if xmi_file is None:
        raise KeyError('XMI file not specified')

    file = parse(f"{UPLOAD_DIR}/user-{user_id}/{xmi_file}")
    xmi = file.firstChild
    # doc = xmi.firstChild
    model = xmi.getElementsByTagName("uml:Model")[0]
    return model.getElementsByTagName("packagedElement")
