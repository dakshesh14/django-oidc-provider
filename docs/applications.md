# Applications

This section covers the applications model and how to create & use them.

## Overview

Applications represent OAuth2 client applications that will use this Django OIDC Provider as their Identity Provider. Each application has unique credentials and configuration for secure authentication.

## Application Model

The `Application` model includes:

- **Name**: Human-readable identifier for the application
- **Client ID**: Auto-generated unique identifier (32 characters)
- **Client Secret**: Auto-generated, hashed secret (shown only once)
- **Redirect URIs**: Newline-separated list of allowed callback URLs
- **Allowed Scopes**: Space-separated OAuth2 scopes (default: "openid email profile")
- **Status**: Active/inactive flag to enable/disable the application

## Creating Applications

### Via Django Admin

1. Create a superuser: `python manage.py createsuperuser`
2. Visit the admin interface at `/admin/`
3. Navigate to **Users** → **Applications**
4. Click **Add Application**
5. Fill in the required details:
   - **Name**: Your application name
   - **Redirect URIs**: One per line (e.g., `https://your-app.com/callback`)
   - **Allowed Scopes**: Space-separated scopes
6. Save the application
7. **Important**: Copy the client secret immediately - it's hashed and cannot be retrieved later

### Required Fields

- `name`: Application identifier
- `redirect_uris`: Valid callback URLs for OAuth2 flow
- `allowed_scopes`: Permissions the application can request

## Configuration

### Redirect URIs

```
https://your-app.com/callback
https://your-app.com/auth/callback
http://localhost:3000/callback
```

### Scopes

Available scopes:

- `openid`: Required for OIDC, enables ID token
- `email`: Access to user's email and verification status
- `profile`: Access to user's profile information

Example: `openid email profile`

## Usage

Applications are used throughout the OAuth2/OIDC flow:

1. **Authorization**: Validates client_id and redirect_uri
2. **Token Exchange**: Authenticates using client_id and client_secret
3. **Scope Validation**: Ensures requested scopes are allowed

## Security Notes

- Client secrets are hashed using Argon2
- Client IDs are cryptographically secure random tokens
- Redirect URIs are strictly validated
- Applications can be deactivated without deletion
