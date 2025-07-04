# Django OIDC Provider Documentation

Welcome to the Django-based OAuth2 and OpenID Connect (OIDC) Identity Provider documentation.

This project provides a complete implementation of an OAuth2 and OpenID Connect Identity Provider using Django, featuring token issuance, user authentication, and user info endpoints.

## Quick Navigation

### Getting Started

- [Getting Started](getting-started.md) - Quick setup and installation guide
- [Development Setup](development.md) - Development environment configuration
- [Application Management](applications.md) - How to create and manage OAuth2 applications

### Core Concepts

- [SSO Flow](sso-flow.md) - Understanding the OAuth2/OIDC authentication flow
- [API Documentation](api/endpoints.md) - REST API endpoints and usage

### Operations

- [Deployment](deployment.md) - Production deployment guide

## Features

- ✅ **OAuth2 Authorization Code Flow** - Complete implementation with PKCE support
- ✅ **OpenID Connect** - User authentication and profile information
- ✅ **JWT Access Tokens** - Secure token-based authentication
- ✅ **Refresh Tokens** - Long-lived authentication sessions
- ✅ **User Registration & Verification** - Email-based user onboarding
- ✅ **Admin Interface** - Django admin for application management
- ✅ **Background Tasks** - Celery integration for email sending
- ✅ **Redis Caching** - Performance optimization with Redis
- ✅ **Docker Support** - Containerized development environment

## Technology Stack

- **Framework**: Django 4.2+
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT tokens
- **API**: Django REST Framework
- **Frontend**: Bootstrap 5

## Standards Compliance

This implementation follows these specifications:

- [RFC 6749 - OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC 6750 - OAuth 2.0 Bearer Token Usage](https://datatracker.ietf.org/doc/html/rfc6750)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)

## Support

For questions, issues, or contributions:

- [GitHub Issues](https://github.com/dakshesh14/django-oidc-provider/issues)

## License

This project is open source. Please check the LICENSE file for details.
