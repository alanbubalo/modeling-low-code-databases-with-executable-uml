"""Generate a Baserow database"""
from app.models import UMLModel
import app.xmi_reader as xr
from app import client
from app.exc import (
    NotAuthorizedException,
    InvalidGroupException,
    InvalidDatabaseException,
    BadFieldException,
    DeletingDatabasesException
)
from app.id_pairs_utils import (
    # find_class_id_for_table,
    find_table_id_for_class,
    create_id_pair,
    # delete_id_pair
)


def validate_group(_group_id: int) -> int:
    """Check if the user has a group with the id provided in env file"""
    group_response = client.list_groups()

    if group_response.status_code != 200:
        raise InvalidGroupException(group_response.json())
    if any(filter(lambda el: el["id"] == _group_id, group_response.json())) is False:
        raise InvalidGroupException(f"Group with id {_group_id} not found")


def validate_database(_database_id: int) -> int:
    """Validate the database"""
    database_response = client.get_application(_database_id)
    if database_response.status_code != 200:
        raise InvalidDatabaseException(database_response.json())


def create_database(_group_id: int, _database_name: str) -> int:
    """Get application by ID"""
    print(f"Creating new database {_database_name}")
    database = client.create_application(_group_id, _database_name, "database").json()
    validate_database(int(database['id']))
    return int(database['id'])


# def try_generate_field(field: dict, table_id: int):
#     """Update a field"""
#     print(field)
#     print(table_id)
#     field_response = client.create_database_table_field(table_id, field)
#     new_field = field_response.json()

#     # Checking for errors
#     if new_field.get('error') == "ERROR_FIELD_WITH_SAME_NAME_ALREADY_EXISTS":
#         print(f"Field {field['name']} already exists")
#         new_field = update_field(field, table_id)
#         print(f"Updated field {new_field['id']} called {new_field['name']}")

#     elif field_response.status_code != 200:
#         raise BadFieldException(new_field)

#     else:
#         print(f"Created new field {new_field['id']} called {new_field['name']}")


# def update_field(_field: dict, _table_id: int) -> dict:
#     """Update field"""
#     list_fields = {
#         _field['name']: _field['id']
#         for _field in client.list_database_table_fields(_table_id).json()}
#     field_id = list_fields[_field["name"]]
#     return client.update_database_table_field(field_id, _field).json()


def create_tables(model_id: int, classes: dict, database_id: int, attributes: dict):
    """Generate tables"""
    for id_, class_ in classes.items():
        class_name = xr.get_class_name(class_)

        # Creating a new table
        new_table = client.create_database_table(database_id, {
            "name": class_name,
            "data": [["Primary key"]],
            "first_row_header": True
        }).json()

        print(f"Table ID: {new_table['id']}")
        print(f"Created table {new_table['name']} with a primary key")

        # Save class and table ids in DB
        create_id_pair(uml_model_id=model_id, class_id=id_, table_id=new_table['id'])

        # Create fields for the table
        for field in attributes[id_]:
            create_field(field, new_table['id'])


# def generate_tables(classes: dict, database_id: int, attributes: dict, id_pairs: list) -> list:
#     """Create tables"""
#     for id_, class_ in classes.items():
#         class_name = xr.get_class_name(class_)
#         table_id = get_baserow_table_id(id_pairs, id_)

#         if not table_id:
#             # ID does not exist, a new table is created
#             print(f"Class with ID {id_} doesn't yet exist in a database")
#             print(f"{get_baserow_table_id(id_pairs, id_)}")

#             # Creating a new table
#             new_table = client.create_database_table(database_id, {
#                 "name": class_name,
#                 "data": [["Primary key"]],
#                 "first_row_header": True
#             }).json()

#             print(f"Table ID: {new_table['id']}")
#             print(f"Created table {new_table['name']} with a primary key")
#         else:
#             # Table already exists in a database
#             print(f"Table called {class_name} already exists")

#             # Get the existing table
#             new_table = client.get_database_table(table_id).json()

#             # Update name of the table
#             if new_table['name'] != class_name:
#                 new_table = client.update_database_table(table_id, class_name).json()

#             print("New table:")
#             print(new_table)

#         # Send both ids to an API server
#         id_pairs.append({'class_id': id_, 'table_id': new_table['id']})
#         print(get_baserow_table_id(id_pairs, id_))

#         # Create fields for the table
#         for field in attributes[id_]:
#             generate_field(field, new_table['id'])

#     return id_pairs


def create_field(field: dict, table_id: int):
    """Generate a new field"""
    print(field)
    print(table_id)
    field_response = client.create_database_table_field(table_id, field)
    new_field = field_response.json()

    # Checking for errors
    if field_response.status_code != 200:
        raise BadFieldException(new_field)
    print(f"Created new field {new_field['id']} called {new_field['name']}")


def create_link_rows(model_id: int, classes: dict, associations: dict):
    """Generate link rows of model"""
    for id_, class_ in classes.items():
        class_name = xr.get_class_name(class_)
        baserow_table_id = find_table_id_for_class(model_id, id_)
        print("Current table:", class_name)
        for association in associations[id_]:
            # Setting new field
            link_row_table_id = find_table_id_for_class(model_id, association['class_id'])
            field = {
                "name": association['name'] or association['class_name'],
                "type": "link_row",
                "link_row_table_id": link_row_table_id
            }

            # Manually setting 'has_related_field' because tables associated
            # with itself must not have this attribute
            if association.get('has_related_field') is not None:
                field["has_related_field"] = association['has_related_field']

            # Create new field
            field_response = client.create_database_table_field(baserow_table_id, field)
            new_field = field_response.json()

            # Checking for errors
            if field_response.status_code != 200:
                raise BadFieldException(new_field)

            print(f"Created new link row field {new_field['id']} called {new_field['name']}")
            # new_field = update_field(field, baserow_table_id)
            print(field)


# def generate_link_rows(classes: dict, associations: dict, id_pairs: list):
#     """Generate link rows"""
#     for id_, class_ in classes.items():
#         class_name = xr.get_class_name(class_)
#         baserow_table_id = get_baserow_table_id(id_pairs, id_)
#         print("Current table:", class_name)
#         for association in associations[id_]:
#             # Setting new field
#             link_row_table_id = get_baserow_table_id(id_pairs, association['class_id'])
#             field = {
#                 "name": association['name'] or association['class_name'],
#                 "type": "link_row",
#                 "link_row_table_id": link_row_table_id
#             }

#             if association.get('has_related_field') is not None:
#                 field["has_related_field"] = association['has_related_field']

#             # Create new field
#             field_response = client.create_database_table_field(baserow_table_id, field)
#             new_field = field_response.json()

#             # Checking for errors
#             if new_field.get('error') == "ERROR_FIELD_WITH_SAME_NAME_ALREADY_EXISTS":
#                 print(f"Link row field {field['name']} already exists")
#                 print(new_field)
#                 # print(f"Updating field {new_field['id']} called {new_field['name']}")

#             elif field_response.status_code != 200:
#                 raise BadFieldException(new_field)

#             else:
#                 print(f"Created new link row field {new_field['id']} called \
# {new_field['name']} in table {class_name}")

#             new_field = update_field(field, baserow_table_id)
#             print(field)


# def delete_table(table_id: int):
#     """Delete a table from Baserow database"""
#     delete_response = client.delete_database_table(table_id)

#     if delete_response.status_code != 204:
#         raise DeletingDatabasesException(delete_response.json())


# def delete_tables(model_id, classes, database_id) -> list:
#     """Remove unused tables from the database"""
#     list_database_tables = client.list_database_tables(database_id).json()
#     # print(f"{list_database_tables = }")

#     for table in list_database_tables:
#         uml_id = find_class_id_for_table(model_id, table['id'])
#         if uml_id not in classes.keys():
#             delete_table(table['id'])

#             print(f"Table {table['id']} named {table['name']} deleted.")
#             print("Looking for...")
#             print({'class_id': uml_id, 'table_id': table['id']})
#             delete_id_pair(IDPair(class_id=uml_id, table_id=table['id'], uml_model_id=model_id))


def create_baserow_database(model: UMLModel) -> int:
    """Generate a new database"""
    # Generate a new database in Baserow
    client.new_session_token(model.baserow_token)

    # print(client)
    if not client.is_token_valid():
        raise NotAuthorizedException("Not authorized to create database")

    # print("Congratulations! You got yourself a token!")

    validate_group(model.group_id)
    # print(f"Group ID: {group_id}")

    database_id = create_database(model.group_id, model.database_name)

    packaged_elements = xr.get_packaged_elements(model.user_id, model.filename)
    classes = xr.get_classes(packaged_elements)
    data_types = xr.get_data_types(packaged_elements)
    enumerations = xr.get_enumerations(packaged_elements)
    associations = xr.get_associations(classes)
    attributes = xr.get_attributes(classes, data_types, enumerations)

    create_tables(model.id, classes, database_id, attributes)

    create_link_rows(model.id, classes, associations)

    return database_id


# def update_baserow_database(
#     user_id: int,
#     group_id: int,
#     baserow_token: str,
#     database_id: int,
#     filename: str,
#     id_pairs: list
# ):
#     """Update the baserow database"""
#     # Generate a new database in Baserow
#     client.new_session_token(baserow_token)

#     # print(client)
#     if not client.is_token_valid():
#         raise NotAuthorizedException("Not authorized to update database")

#     # print("Congratulations! You got yourself a token!")

#     validate_group(group_id)
#     # print(f"Group ID: {group_id}")

#     validate_database(database_id)

#     # Get information from XMI file
#     packaged_elements = xr.get_packaged_elements(user_id, filename)
#     classes = xr.get_classes(packaged_elements)
#     data_types = xr.get_data_types(packaged_elements)
#     enumerations = xr.get_enumerations(packaged_elements)
#     associations = xr.get_associations(classes)
#     attributes = xr.get_attributes(classes, data_types, enumerations)

#     # Create tables
#     id_pairs = generate_tables(classes, database_id, attributes, id_pairs)

#     # Add Link Rows in tables
#     generate_link_rows(classes, associations, id_pairs)

#     # Remove
#     id_pairs = remove_tables(classes, database_id, id_pairs)

#     return id_pairs


def delete_baserow_database(model: UMLModel):
    """Delete a baserow database"""
    client.new_session_token(model.baserow_token)
    if not client.is_token_valid():
        raise NotAuthorizedException("Not authorized to update database")

    validate_group(model.group_id)
    validate_database(model.database_id)

    delete_db_response = client.delete_application(model.database_id)
    if delete_db_response.status_code != 204:
        raise DeletingDatabasesException(delete_db_response.json())
