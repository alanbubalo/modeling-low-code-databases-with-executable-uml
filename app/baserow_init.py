"""Generate a Baserow database"""
import app.xmi_reader as xr
from app import client


def validate_group(_group_id: int) -> int:
    """Check if the user has a group with the id provided in env file"""
    groups = client.list_groups().json()

    if isinstance(groups, dict) and groups.get('error'):
        raise Exception(groups)

    next(filter(lambda el: el["id"] == _group_id, groups))

    return _group_id


def validate_database(_database_id: int) -> int:
    """Validate the database"""
    database = client.get_application(_database_id).json()
    if database.get('error'):
        raise Exception(database)
    return _database_id


def create_database(_group_id: int, _database_name: str) -> int:
    """Get application by ID"""
    # Create a new database and get its ID
    # DATABASE_ID = input_.DATABASE_ID # os.getenv('DATABASE_ID')

    # if bool(DATABASE_ID) == bool(DATABASE_NAME):
    #     raise Exception("Either DATABASE_NAME or DATABASE_ID must be specified")

    print(f"Creating new database {_database_name}")
    database = client.create_application(_group_id, _database_name, "database").json()
    database_id = validate_database(int(database['id']))
    return database_id


def generate_field(field, new_table):
    """Generate a new field"""
    print(field)
    print(new_table['id'])
    field_response = client.create_database_table_field(new_table["id"], field)
    new_field = field_response.json()

    # Checking for errors
    if new_field.get('error') == "ERROR_FIELD_WITH_SAME_NAME_ALREADY_EXISTS":
        print(f"Field {field['name']} already exists")
        new_field = update_field(field, new_table['id'])
        print(f"Updated field {new_field['id']} called {new_field['name']}")

    elif field_response.status_code != 200:
        raise Exception(new_field)

    else:
        print(f"Created new field {new_field['id']} called {new_field['name']}")


def update_field(_table_id: int, _field: dict) -> dict:
    """Update field"""
    list_fields = {
        _field['name']: _field['id']
        for _field in client.list_database_table_fields(_table_id).json()}
    field_id = list_fields[_field["name"]]
    return client.update_database_table_field(field_id, _field).json()


def get_baserow_table_id(id_pairs, class_id):
    """Get table ID from Baserow with class ID"""
    for pair in id_pairs:
        if pair['class_id'] == class_id:
            return pair['table_id']
    return None


def get_uml_class_id(id_pairs, table_id):
    """Get class ID from UML class diagram with table ID"""
    for pair in id_pairs:
        if pair['table_id'] == table_id:
            return pair['class_id']
    return None


def generate_tables(classes, database_id, attributes, id_pairs: list) -> list:
    """Create tables"""
    for id_, class_ in classes.items():
        class_name = class_.getAttribute('name').replace('%20', ' ')
        table_id = get_baserow_table_id(id_pairs, id_)

        if not table_id:
            # ID does not exist, a new table is created
            print(f"Class with ID {id_} doesn't yet exist in a database")
            print(f"{get_baserow_table_id(id_pairs, id_)}")

            # Creating a new table
            new_table = client.create_database_table(database_id, {
                "name": class_name,
                "data": [["Primary key"]],
                "first_row_header": True
            }).json()

            print(f"Table ID: {new_table['id']}")
            print(f"Created table {new_table['name']} with a primary key")
        else:
            # Table already exists in a database
            print(f"Table called {class_name} already exists")

            # Get the existing table
            new_table = client.get_database_table(table_id).json()

            # Update name of the table
            if new_table['name'] != class_name:
                new_table = client.update_database_table(table_id, class_name).json()

        # Send both ids to an API server
        id_pairs.append({'class_id': id_, 'table_id': new_table['id']})
        print(get_baserow_table_id(id_pairs, id_))

        # Create fields for the table
        for field in attributes[id_]:
            generate_field(field, new_table)

    return id_pairs


def generate_link_rows(classes, associations, id_pairs):
    """Generate link rows"""
    for id_, class_ in classes.items():
        class_name = class_.getAttribute('name').replace('%20', ' ')
        baserow_table_id = get_baserow_table_id(id_pairs, id_)
        print("Current table:", class_name)
        for association in associations[id_]:
            # Setting new field
            link_row_table_id = get_baserow_table_id(id_pairs, association['class_id'])
            field = {
                "name": association['name'] or association['class_name'],
                "type": "link_row",
                "link_row_table_id": link_row_table_id
            }

            if association.get('has_related_field'):
                field["has_related_field"] = association['has_related_field']

            # Create new field
            field_response = client.create_database_table_field(baserow_table_id, field)
            new_field = field_response.json()

            # Checking for errors
            if new_field.get('error') == "ERROR_FIELD_WITH_SAME_NAME_ALREADY_EXISTS":
                print(f"Link row field {field['name']} already exists")
                new_field = update_field(baserow_table_id, field)
                print(new_field)
                print(f"Updated field {new_field['id']} called {new_field['name']}")

            elif field_response.status_code != 200:
                raise Exception(new_field)

            else:
                print(f"Created new link row field {new_field['id']} called \
{new_field['name']} in table {class_name}")


def remove_tables(classes, database_id, id_pairs: list) -> list:
    """Remove unused tables from the database"""
    list_database_tables = client.list_database_tables(database_id).json()
    # print(f"{list_database_tables = }")

    for table in list_database_tables:
        uml_id = get_uml_class_id(id_pairs, table['id'])
        if uml_id not in classes.keys():
            client.delete_database_table(table['id'])
            print(f"Table {table['id']} named {table['name']} deleted.")
            id_pairs.remove({'class_id': uml_id, 'table_id': table['id']})

    return id_pairs


def create_baserow_database(
    user_id: int,
    group_id: int,
    baserow_token: str,
    database_name: str,
    filename: str,
    id_pairs: list
):
    """Generate a new database"""
    # Generate a new database in Baserow
    client.new_session_token(baserow_token)

    # print(client)
    if not client.is_token_valid():
        raise Exception("Not authorized to create database")

    # print("Congratulations! You got yourself a token!")

    group_id = validate_group(group_id)
    # print(f"Group ID: {group_id}")

    database_id = create_database(group_id, database_name)
    database_id = validate_database(database_id)

    packaged_elements = xr.get_packaged_elements(user_id, filename)
    classes = xr.get_classes(packaged_elements)
    data_types = xr.get_data_types(packaged_elements)
    enumerations = xr.get_enumerations(packaged_elements)
    associations = xr.get_associations(classes)
    attributes = xr.get_attributes(classes, data_types, enumerations)

    print(f"{packaged_elements = }")
    print(f"{classes = }")
    print(f"{data_types = }")
    print(f"{enumerations = }")
    print(f"{associations = }")
    print(f"{attributes = }")

    return None

    # Create tables
    id_pairs = generate_tables(classes, database_id, attributes, id_pairs)

    # Add Link Rows in tables
    generate_link_rows(classes, associations, id_pairs)

    return id_pairs, database_id


def update_baserow_database(
    user_id: int,
    group_id: int,
    baserow_token: str,
    database_id: int,
    filename: str,
    id_pairs: list
):
    """Update the baserow database"""
    # Generate a new database in Baserow
    client.new_session_token(baserow_token)

    # print(client)
    if not client.is_token_valid():
        raise Exception("Not authorized to update database")

    # print("Congratulations! You got yourself a token!")

    group_id = validate_group(group_id)
    # print(f"Group ID: {group_id}")

    database_id = validate_database(database_id)

    # Get information from XMI file
    packaged_elements = xr.get_packaged_elements(user_id, filename)
    classes = xr.get_classes(packaged_elements)
    data_types = xr.get_data_types(packaged_elements)
    enumerations = xr.get_enumerations(packaged_elements)
    associations = xr.get_associations(classes)
    attributes = xr.get_attributes(classes, data_types, enumerations)

    # Create tables
    id_pairs = generate_tables(classes, database_id, attributes, id_pairs)

    # Add Link Rows in tables
    generate_link_rows(classes, associations, id_pairs)

    # Remove
    id_pairs = remove_tables(classes, database_id, id_pairs)

    return id_pairs


def delete_baserow_database(
    group_id: int,
    baserow_token: str,
    database_id: int,
):
    """Delete a baserow database"""
    client.new_session_token(baserow_token)

    # print(client)
    if not client.is_token_valid():
        raise Exception("Not authorized to update database")

    # print("Congratulations! You got yourself a token!")

    group_id = validate_group(group_id)
    database_id = validate_database(database_id)

    deleted_database = client.delete_application(database_id).json()
    if deleted_database.get('error'):
        raise Exception(deleted_database)
