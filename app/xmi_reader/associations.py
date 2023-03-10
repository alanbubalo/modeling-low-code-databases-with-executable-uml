"""Generates a dictionary with lists of associations for each class. """
from xml.dom.minidom import Element


def get_navigable(end: Element) -> bool | None:
    """
    Returns a boolean value of end's attribute 'is_navigable' or `None` if the attribute not
    defined.
    """
    if end.getAttribute("isNavigable") == "true":
        return True
    if end.getAttribute("isNavigable") == "false":
        return False
    return None


def solve_navigable(ends: list[dict],
                    class_id: str,
                    class_associations: dict[str, list]
) -> None:
    """Filters and adds ends to the class associations dictionary.

    Args:
        ends (list[dict]): a list of ends in an association
        class_id (str): current class
        class_associations (dict[str, list]): dictionary for storing associations of each class
    """
    # for end in ends:
    #     print(end)
    # print(class_id)

    # First easy case is if a class is associated with itself
    # If both ends have the same class ID
    if all(end["class_id"] == class_id for end in ends):
        # it doesn't matter which end is added since both are the same
        class_associations[class_id].append(ends[0])
        # print("Case 1")
        return

    # Second easy case is if a class has association with an end that has current class' ID,
    # if there is both or no direction in the association
    # Then we take one class, connect to another, has_related_field is True
    ends_class_matches = (end["class_id"] == class_id for end in ends)
    # ends_class_non_matches = (end["class_id"] != class_id for end in ends)
    assoc_has_itself = any(ends_class_matches) # and any(ends_class_non_matches)

    all_navigable = all(end['is_navigable'] is True for end in ends)
    all_unspecified = all(end['is_navigable'] is None for end in ends)

    if assoc_has_itself and (all_navigable or all_unspecified):
        other_end = ends[0] if ends[0]['class_id'] != class_id else ends[1]
        other_end['has_related_field'] = True
        class_associations[class_id].append(other_end)
        # print("Case 2")
        return

    # Third case is if association connect to two different classes
    # If there is such, navigation should be the same? or not... ?
    if all(end["class_id"] != class_id for end in ends):
        ends[0]['has_related_field'] = ends[0]['is_navigable'] is None
        ends[1]['has_related_field'] = ends[1]['is_navigable'] is None
        class_associations[class_id].append(ends[0])
        class_associations[class_id].append(ends[1])
        # print("Case 3")
        return

    # Last case is if association has one direction and
    # class has only one end on itself
    other_id = next(iter({end['class_id'] for end in ends} - {class_id}))
    if ends[0]['is_navigable']:
        ends[0]['has_related_field'] = False
        class_associations[other_id].append(ends[0])
    else:
        ends[1]['has_related_field'] = False
        class_associations[class_id].append(ends[1])
    # print("Case 4")


def get_class_name(class_: Element) -> str:
    """Get the filtered name of the given class 

    Args:
        class_ (Element): current class

    Returns:
        str: filtered name of the class
    """
    return class_.getAttribute('name').replace('%20', '_').lower()


def get_associations(classes: dict[str, Element]) -> dict[str, list]:
    """Generates a dictionary with lists of associations for each class.

    Args:
        classes (dict[str, Element]): a dictionary of classes

    Returns:
        dict[str, list]: a new dictionary with lists of associations for each class
    """
    class_associations = {id: [] for id in classes.keys()}

    for id_, class_ in classes.items():
        # print("---------------------------------------------------------")
        # print()
        # print("CLASS:", get_class_name(classes[id_]))
        # print()
        owned_members = class_.getElementsByTagName("ownedMember")
        owned_ends = (member.getElementsByTagName("ownedEnd") for member in owned_members)

        for pair in owned_ends:
            ends = [{
                "name": curr.getAttribute("name").title().replace("_", " "),
                "class_id": curr.getAttribute("type"),
                "class_name": get_class_name(classes[curr.getAttribute("type")]),
                "aggregation": curr.getAttribute("aggregation"),
                "is_navigable": get_navigable(curr)
            } for curr in pair]

            solve_navigable(ends, id_, class_associations)

            # for class_id, assoc in class_associations.items():
            #     print(get_class_name(classes[class_id]), "->", assoc)
            # print()

    return class_associations
