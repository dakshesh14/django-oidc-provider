# Django OIDC Provider

A Django implementation of an OAuth2 and OpenID Connect (OIDC) Identity Provider, featuring token issuance, user authentication, and user info endpoints.

https://github.com/user-attachments/assets/35854c0b-6434-4f5e-a6d9-08b13ee7d287

## Features

- ✅ **OAuth2 Authorization Code Flow** - Complete implementation with PKCE support
- ✅ **OpenID Connect** - User authentication and profile information
- ✅ **JWT Access Tokens** - Secure token-based authentication
- ✅ **Refresh Tokens** - Long-lived authentication sessions
- ✅ **User Registration & Verification** - Email-based user onboarding
- ✅ **Admin Interface** - Django admin for application management
- ✅ **Background Tasks** - Celery integration for email sending
- ✅ **Docker Support** - Containerized development environment

## Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/<your_username>/django-oidc-provider.git
   cd django-oidc-provider
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements/local.txt
   ```

3. **Set up pre-commit hooks:**

   ```bash
   pre-commit install
   ```

4. **Follow the complete setup guide:** [Getting Started](docs/getting-started.md)

## Documentation

- 📖 **[Getting Started](docs/getting-started.md)** - Complete installation and setup guide
- 🔐 **[SSO Flow](docs/sso-flow.md)** - Understanding the OAuth2/OIDC authentication flow
- 📱 **[Applications](docs/applications.md)** - How to create and manage OAuth2 applications
- 🛠️ **[Development](docs/development.md)** - Development environment and workflow
- 🚀 **[API Documentation](docs/api/endpoints.md)** - REST API endpoints and usage
- 📋 **[Full Documentation](docs/index.md)** - Complete documentation index

## Standards Compliance

This implementation follows:

- [RFC 6749 - OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC 6750 - OAuth 2.0 Bearer Token Usage](https://datatracker.ietf.org/doc/html/rfc6750)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

## Future Plans

- [ ] Add discovery endpoints
- [ ] Add JWKS support
- [ ] Improve error handling
- [ ] Add more application types

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

Thanks to the amazing open-source community and the Django ecosystem that made this project possible.

---

**Author:** [Dakshesh Jain](https://dakshesh.me)
**Connect:** [LinkedIn](https://www.linkedin.com/in/dakshesh-jain/) • [Twitter](https://twitter.com/_dakshesh) • [GitHub](https://github.com/dakshesh14)

_If you find this project useful, please consider giving it a star! ⭐_
