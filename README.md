# REST API

## Introduction

REST API for transforming UML class diagram into Baserow database.

## API routes

### Basic API test call

A basic REST API call for testing functionality of the application.

#### Request

`GET /api/v1/test`

```bash
curl -i http://127.0.0.1:5000/test
```

#### Response

```bash
HTTP/1.1 200 OK
Date: Thu, 24 Feb 2023 12:36:30 GMT
Status: 200 OK
Connection: close
Content-Type: application/json
Content-Length: 22

{data: {"Test works"}}
```
