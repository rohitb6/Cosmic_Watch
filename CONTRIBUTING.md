# Contribution Guidelines

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/cosmic-watch.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Set up development environment (see README.md)

## Development Process

### Backend Changes
```bash
cd backend
# Install dev dependencies
pip install -r requirements.txt
pytest  # Run tests before committing
```

### Frontend Changes
```bash
cd frontend
npm install
npm run dev  # Start dev server
npm test     # Run tests
npm run lint # Check code style
```

### Code Style
- **Python**: Follow PEP 8 (use `black` for formatting)
- **TypeScript**: Follow Prettier configuration
- **Commit messages**: Use conventional commits
  ```
  feat: add new risk scoring factor
  fix: resolve null pointer in CRI calculation
  docs: update API documentation
  ```

## Testing Requirements

- Backend: Maintain 70%+ test coverage
- Frontend: Maintain 50%+ test coverage
- New features must include tests

## Pull Request Process

1. Update relevant documentation
2. Add tests for new functionality
3. Ensure all tests pass: `docker-compose exec backend pytest`
4. Update CHANGELOG.md
5. Create PR with clear description
6. Request review from maintainers

## Reporting Bugs

Include:
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Environment info (OS, Docker version, etc.)
- Logs and error messages

## Suggesting Features

Use GitHub Discussions or Issues with:
- Clear use case
- Why it's important for Cosmic Watch
- Suggested implementation approach
- Any related references

Thank you for contributing! 🚀
