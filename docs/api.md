# pickal — API Documentation

## Overview

This document describes the API endpoints and data structures for pickal.

## Authentication

Authentication is handled via API keys or OAuth2 tokens.

## Endpoints

### Health Check

```
GET /health
```

Returns the health status of the application.

### Configuration

```
GET /config
```

Returns the current configuration (sanitized for security).

### Version

```
GET /version
```

Returns the application version information.

## Data Structures

### Response Format

All responses are returned in JSON format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "timestamp": "2023-01-01T00:00:00Z"
}
```

### Error Format

Errors are returned with a consistent format:

```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Error message",
    "details": { ... }
  },
  "timestamp": "2023-01-01T00:00:00Z"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

## Rate Limiting

API endpoints are rate limited to prevent abuse.

## Versioning

API versions are managed through URL paths: `/v1/*`

## Examples

### Health Check

```bash
curl -X GET http://localhost:8080/health
```

Response:

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2023-01-01T00:00:00Z"
  }
}
```