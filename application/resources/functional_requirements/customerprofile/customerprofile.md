# CustomerProfile Entity

## Overview
CustomerProfile represents a business entity undergoing regulatory onboarding with comprehensive identity, ownership, and risk information.

## Attributes

### Identity
- **legalName**: Official registered business name
- **tradingName**: Trading or DBA name (optional)
- **registrationId**: Business registration number
- **taxId**: Tax identification number
- **countryOfIncorporation**: Country where business is incorporated

### OwnershipGraph
Nested structure representing beneficial ownership:
- **percentOwnership**: Ownership percentage (0-100)
- **controlFlags**: Array of control indicators (voting, board, management)
- **residency**: Owner's country of residence
- **children**: Array of sub-owners for multi-level ownership
- **ultimateBeneficiaryFlag**: Indicates if this is an ultimate beneficial owner

### Contacts
- **emails**: Array with email, label, verificationStatus
- **phones**: Array with number, label, verificationStatus

### Addresses
- **type**: Address type (registered, operational, mailing)
- **lines**: Array of address lines
- **locality**: City/town
- **region**: State/province
- **postalCode**: Postal/ZIP code
- **country**: Country code
- **geoCode**: Latitude/longitude coordinates

### KYCArtifacts
- **type**: Document type (certificate, passport, utility_bill)
- **fileRef**: Reference to uploaded file
- **hash**: Document hash for integrity
- **issuer**: Issuing authority
- **issueDate**: Document issue date
- **expiryDate**: Document expiry date
- **verificationResult**: Verification status
- **revisionHistory**: Array of document versions

### Risk
- **riskScore**: Numerical risk score (0-100)
- **riskFactors**: Array of identified risk factors
- **pepFlags**: Politically Exposed Person indicators
- **sanctionsHits**: Array of sanctions screening results with dispositions

## State Management
Entity state is managed internally via `entity.meta.state` and should not appear in the entity schema. States include: Draft, Submitted, InReview, PendingDocs, Approved, Rejected, Archived.

## Relationships
CustomerProfile is a standalone entity with internal ownership relationships through the OwnershipGraph structure.
