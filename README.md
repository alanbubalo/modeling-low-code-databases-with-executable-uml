# REST API

## Introduction

REST API for transforming UML class diagram into Baserow database.

UML class diagram as an XMI file is parsed in Python and then a database is created with all tables as classes, fields as attributes, enumerations and associations from a model.

## Limitations

Supported versions

- XMI: 2.1
- UML: 2.0

API is currently adjusted to XMI models exported from StarUML software's extension.

## Use cases

- Add, reupload, rename and delete XMI files
- Generate and manage multiple databases in Baserow from uploaded UML models
- CRUD operations on table data

## Basic use cases

### Create user

You can create an account to keep your models' metadata and files safe.

Example:

```python
response = requests.post(
    f'{url}/api/v1/users',
    json={
        'email': email,
        'password': password
    },
    header={'Content-Type': 'application/json'})
```

Make sure to retrieve access and refresh token from the response and put them in the header.

Example:

```python
response = requests.get(
    f'{url}/api/v1/test_protected',
    header={'Authorization': f'Bearer {access_token}'})
```

### Upload XMI files

Upload XMI files with REST API to save them and attach them to the model.

Example:

```python
response = requests.put(
    f'{url}/api/v1/files/{filename}',
    data=xmi_file,
    header={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/xml'
    })
```

### Create model and generate database

Creating a new model, API gathers information from the uploaded XMI file and generates a database in Baserow.

Example:

```python
response = requests.post(
    f'{url}/api/v1/models',
    json={
        'database_url': database_name, # provide if baserow is self hosted
        'database_name': database_name,
        'baserow_token': refresh_token,
        'group_id': group_id,
        'filename': filename
    },
    header={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    })
```

### Update the database with one request

You can update the database with one request. When updating model information, one more request is necessary to confirm the change in Baserow.

Example:

```python
response = requests.patch(
    f'{url}/api/v1/models/{model_id}',
    header={'Authorization': f'Bearer {access_token}'})
```

### CRUD operations on Baserow tables

Directly access and manage data within each table in your model.

Example:

```python
response = requests.post(
    f'{url}/api/v1/data/model/{model_id}/table/{table_name}',
    json={
        'field_1': data_1,
        'field_2': data_2,
        'field_3': data_3
    },
    header={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    })
```
