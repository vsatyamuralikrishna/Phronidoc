# API Documentation Template

**Template for documenting APIs, endpoints, and SDKs**

---

## API Name

**Version:** `1.0.0`  
**Base URL:** `https://api.example.com/v1`  
**Last Updated:** `YYYY-MM-DD`  
**Author:** `Your Name`

## Overview

Brief description of what this API does and its main purpose.

### Key Features

- Feature 1
- Feature 2
- Feature 3

## Authentication

Describe the authentication method used (API keys, OAuth, JWT, etc.).

```bash
# Example authentication header
Authorization: Bearer YOUR_API_KEY
```

## Base URL

```
https://api.example.com/v1
```

## Endpoints

### Endpoint Name

**Description:** Brief description of what this endpoint does.

**Method:** `GET|POST|PUT|DELETE|PATCH`

**URL:** `/endpoint/path`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `param1` | string | Yes | Description of parameter |
| `param2` | integer | No | Description of parameter |

**Request Example:**

```bash
curl -X GET "https://api.example.com/v1/endpoint/path?param1=value" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Request Body (if applicable):**

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Response Example:**

```json
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "Example"
  }
}
```

**Response Codes:**

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request |
| `401` | Unauthorized |
| `404` | Not Found |
| `500` | Internal Server Error |

**Error Response:**

```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

---

## SDK Examples

### JavaScript/TypeScript

```javascript
import { ApiClient } from '@example/api-client';

const client = new ApiClient('YOUR_API_KEY');
const result = await client.getEndpoint({ param1: 'value' });
```

### Python

```python
from example_api import ApiClient

client = ApiClient(api_key='YOUR_API_KEY')
result = client.get_endpoint(param1='value')
```

---

## Rate Limiting

Describe rate limiting policies if applicable.

- **Limit:** X requests per minute
- **Headers:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | YYYY-MM-DD | Initial release |

## Related Documentation

- [Architecture Documentation](../engineering/architecture/)
- [Authentication Guide](../engineering/authentication/)
- [SDK Documentation](../engineering/sdks/)

---

**Template Instructions:**
1. Replace all placeholder text with actual content
2. Add or remove endpoints as needed
3. Include actual code examples
4. Update version numbers and dates
5. Add links to related documentation
