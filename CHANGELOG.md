# Changelog

All notable changes to Guaro are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Auto-migration system with non-destructive schema updates
- Support for SQLite, PostgreSQL, MySQL, and MongoDB
- GraphQL schema generation via Strawberry
- REST routing with full HTTP method support
- Dependency injection framework
- Model relationships (one-to-many)
- Field selection for optimized queries
- Middleware and authentication support
- Comprehensive documentation suite

### Changed
- Relation fields now excluded from database schema
- Route handlers converted to async
- Improved error handling in lifecycle events

### Fixed
- MySQL VARCHAR length requirement (now uses VARCHAR(255))
- Auto migrate config flag now respected
- Silent error handling in adapter connections

## [0.2.0] - 2026-06-02
- Prepare release 0.2.0: package metadata bump and minor fixes.
- Updated security handling and logging improvements.
- Updated documentation and CI configuration.

## [Roadmap]

### Planned for v0.2.0
- [ ] Alembic integration for advanced migrations
- [ ] Database connection pooling optimization
- [ ] Caching layer with Redis support
- [ ] Background task support (Celery integration)
- [ ] API documentation generation (OpenAPI/Swagger)
- [ ] Request/response schemas

### Planned for v0.3.0
- [ ] File upload handling
- [ ] WebSocket support
- [ ] Server-Sent Events (SSE)
- [ ] Subscription support for GraphQL
- [ ] Rate limiting middleware

### Planned for v1.0.0
- [ ] Stable API guarantee
- [ ] Performance optimizations
- [ ] Extended test coverage (95%+)
- [ ] Production deployment guides
- [ ] Docker integration examples

## How to Read This Changelog

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security updates

## Versioning

Guaro follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

## See Also

- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Development Guide](docs/DEVELOPMENT.md) - Internal architecture
- [GitHub Releases](https://github.com/Alazar42/Guaro/releases) - Release notes
