# CustomerProfile API Routes

## Overview
REST API endpoints for CustomerProfile entity management and workflow operations.

## Base Route
`/api/customerprofile`

## Endpoints

### Create CustomerProfile
**POST** `/api/customerprofile`

Creates a new customer profile in Draft state.

**Request Body:**
```json
{
  "identity": {
    "legalName": "Acme Corporation Ltd",
    "tradingName": "Acme Corp",
    "registrationId": "12345678",
    "taxId": "GB123456789",
    "countryOfIncorporation": "GB"
  },
  "contacts": {
    "emails": [{"email": "contact@acme.com", "label": "primary", "verificationStatus": "pending"}],
    "phones": [{"number": "+44123456789", "label": "main", "verificationStatus": "pending"}]
  },
  "addresses": [{
    "type": "registered",
    "lines": ["123 Business Street"],
    "locality": "London",
    "region": "England",
    "postalCode": "SW1A 1AA",
    "country": "GB"
  }]
}
```

**Response:**
```json
{
  "id": "cp_123456789",
  "status": "created",
  "state": "draft"
}
```

### Get CustomerProfile
**GET** `/api/customerprofile/{id}`

**Response:**
```json
{
  "id": "cp_123456789",
  "identity": {...},
  "ownershipGraph": [...],
  "contacts": {...},
  "addresses": [...],
  "kycArtifacts": {...},
  "risk": {...},
  "meta": {
    "state": "draft",
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  }
}
```

### Update CustomerProfile
**PUT** `/api/customerprofile/{id}`

**Request Body:**
```json
{
  "identity": {...},
  "transition": "submit_profile"
}
```

**Response:**
```json
{
  "id": "cp_123456789",
  "status": "updated",
  "state": "submitted"
}
```

### Upload Document
**POST** `/api/customerprofile/{id}/documents`

**Request Body (multipart/form-data):**
```
file: [binary file data]
type: "certificate_of_incorporation"
issuer: "Companies House"
issueDate: "2020-01-15"
expiryDate: "2025-01-15"
```

**Response:**
```json
{
  "documentId": "doc_987654321",
  "status": "uploaded",
  "hash": "sha256:abc123...",
  "verificationStatus": "pending"
}
```

### Transition State
**POST** `/api/customerprofile/{id}/transition`

**Request Body:**
```json
{
  "transition": "approve_profile",
  "reason": "All checks passed",
  "actor": "compliance_officer_123"
}
```

**Response:**
```json
{
  "id": "cp_123456789",
  "previousState": "inreview",
  "newState": "approved",
  "transitionedAt": "2024-01-20T14:30:00Z"
}
```

### List CustomerProfiles
**GET** `/api/customerprofile?state=inreview&limit=50&offset=0`

**Response:**
```json
{
  "profiles": [
    {
      "id": "cp_123456789",
      "identity": {"legalName": "Acme Corporation Ltd"},
      "meta": {"state": "inreview", "updatedAt": "2024-01-20T10:00:00Z"}
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### Delete CustomerProfile
**DELETE** `/api/customerprofile/{id}`

**Response:**
```json
{
  "id": "cp_123456789",
  "status": "deleted"
}
```
