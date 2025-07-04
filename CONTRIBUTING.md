# Contributing to Django OIDC Provider

Thank you for your interest in contributing! 🎉 We welcome contributions from everyone, whether you're fixing a bug, adding a feature, or improving documentation.

## Getting Started

1. **Fork the repository** and clone your fork
2. **Set up the development environment** following our [Development Guide](docs/development.md)
3. **Install pre-commit hooks** (required):
   ```bash
   pre-commit install
   ```

## How to Contribute

### 🐛 Reporting Issues

- Use the GitHub issue tracker
- Search existing issues first to avoid duplicates
- Provide clear steps to reproduce the problem
- Include relevant system information (OS, Python version, etc.)

### 💡 Suggesting Features

- Open an issue with the "enhancement" label
- Describe the feature and its use case
- Discuss the implementation approach if you have ideas

### 🔧 Submitting Changes

1. **Create a new branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes** following our coding standards
3. **Write or update tests** if applicable
4. **Run pre-commit checks**:
   ```bash
   pre-commit run --all-files
   ```
5. **Commit your changes** using Angular-style commit messages
6. **Push your branch** and create a pull request

## Branch Naming

Use descriptive branch names with prefixes:

- `feature/add-oauth-scopes` - New features
- `fix/token-expiry-bug` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/auth-flow` - Code refactoring
- `test/application-model` - Test improvements

## Commit Message Format

We use Angular-style commit messages:

```
type(scope): short description

Longer description if needed

Fixes #123
```

### Types

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style/formatting (no logic changes)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(auth): add PKCE support for OAuth2 flow

fix(tokens): resolve token expiry validation bug

docs(readme): update installation instructions

test(models): add tests for Application model
```

## Code Standards

- **Pre-commit hooks are mandatory** - they handle formatting and linting
- Follow existing code style and patterns
- Write clear, self-documenting code
- Add docstrings for new functions and classes
- Keep functions small and focused

## Development Workflow

1. **Development setup**: Follow [docs/development.md](docs/development.md)
2. **Run tests**: `python manage.py test`
3. **Code quality**: Pre-commit hooks will run automatically
4. **Manual checks**: `pre-commit run --all-files`

## Pull Request Guidelines

### Before Submitting

- [ ] Pre-commit hooks pass
- [ ] Tests pass locally
- [ ] Code follows project conventions
- [ ] Documentation updated if needed

### PR Description

Please include:

- **What**: Brief summary of changes
- **Why**: Reason for the change
- **How**: Implementation approach (if complex)
- **Testing**: How you tested the changes
- **Screenshots**: For UI changes

### Review Process

- All PRs require review before merging
- Address review feedback promptly
- Keep PRs focused and reasonably sized
- Maintain a friendly, collaborative tone

## Code of Conduct

- **Be respectful** and inclusive
- **Be patient** with new contributors
- **Be constructive** in feedback
- **Be open** to different perspectives

## Questions?

- Open an issue for questions
- Check existing documentation first
- Ask for help - we're here to support you!

## Recognition

Contributors will be acknowledged in our project. Thank you for making this project better! 🙏

---

_Happy contributing!_ 🚀
