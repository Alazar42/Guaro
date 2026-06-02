# Documentation Index

Welcome to Guaro's developer documentation. Start here to find what you need.

## Getting Started

### [Installation Guide](INSTALLATION.md)
**Time: 5 minutes** | Get Guaro installed and configured for your database.
- Requirements and installation methods
- Quick setup walkthrough
- Database configuration examples
- Environment variables

**Best for: First time setup**

### [Models Guide](MODELS.md)
**Time: 10 minutes** | Define your data models.
- Model definition basics
- Field types reference
- Relationships and primary keys
- Model methods (CRUD operations)
- Auto-migration explanation

**Best for: Defining your first model**

### [Routing Guide](ROUTING.md)
**Time: 15 minutes** | Create REST API endpoints.
- Router setup
- HTTP methods (GET, POST, PUT, DELETE)
- Path and query parameters
- Request bodies and responses
- Field selection
- Error handling and status codes

**Best for: Building REST endpoints**

## Core Concepts

### [Database Configuration](DATABASE.md)
**Time: 20 minutes** | Support for multiple databases.
- All supported databases (SQLite, PostgreSQL, MySQL, MongoDB)
- Three connection methods
- Database-specific setup guides
- Connection pooling and performance
- Production best practices

**Best for: Choosing/configuring a database**

### [GraphQL Guide](GRAPHQL.md)
**Time: 10 minutes** | Expose your API through GraphQL.
- Automatic schema generation
- Queries and mutations
- Field selection
- Relationships and dataloaders
- Performance optimization

**Best for: Adding GraphQL to your API**

### [Middleware & Authentication](MIDDLEWARE.md)
**Time: 15 minutes** | Secure your API.
- Basic middleware setup
- Authorization and permissions
- User authentication
- JWT tokens
- CORS, rate limiting, logging
- Security best practices

**Best for: Adding authentication and security**

### [Dependency Injection](DEPENDENCY_INJECTION.md)
**Time: 15 minutes** | Advanced service management.
- Service registration and injection
- Service lifetimes (transient, singleton, scoped)
- Service factories
- Repository pattern
- Testing with mocks
- Common architectural patterns

**Best for: Building scalable applications**

## Development & Contribution

### [Development Guide](DEVELOPMENT.md)
**Time: 20 minutes** | Contribute to Guaro.
- Prerequisites and environment setup
- Project structure
- Code style guidelines
- Testing procedures
- Debugging and profiling
- Contribution guidelines

**Best for: Contributing to Guaro or understanding internals**

## Quick Reference

### Common Tasks

**Set up a new project:**
1. Follow [Installation Guide](INSTALLATION.md)
2. Define models in [Models Guide](MODELS.md)
3. Create routes in [Routing Guide](ROUTING.md)

**Add a database:**
1. Choose from [Database Configuration](DATABASE.md)
2. Update config in `.env` or `config.py`
3. Guaro auto-migrates schema

**Secure your API:**
1. Follow [Middleware & Authentication](MIDDLEWARE.md)
2. Add JWT validation
3. Implement permission checks

**Scale with services:**
1. Use [Dependency Injection](DEPENDENCY_INJECTION.md)
2. Create repository layer
3. Inject in routes

**Expose GraphQL:**
1. Register models
2. Follow [GraphQL Guide](GRAPHQL.md)
3. Test in GraphQL Playground

### Learning Path

**Beginner (1-2 hours):**
1. [Installation](INSTALLATION.md)
2. [Models](MODELS.md)
3. [Routing](ROUTING.md)
→ You can build basic REST APIs

**Intermediate (2-4 hours):**
4. [Database Configuration](DATABASE.md) - Choose your DB
5. [Middleware & Authentication](MIDDLEWARE.md) - Secure your app
6. [GraphQL Guide](GRAPHQL.md) - Modern API alternative
→ You can build production REST/GraphQL APIs

**Advanced (4+ hours):**
7. [Dependency Injection](DEPENDENCY_INJECTION.md) - Build scalable code
8. [Development Guide](DEVELOPMENT.md) - Internals and testing
→ You can contribute to Guaro and build enterprise applications

## External Resources

### Frameworks & Libraries Used
- [Starlette](https://www.starlette.io/) - ASGI web framework
- [SQLAlchemy](https://docs.sqlalchemy.org/) - SQL toolkit and ORM
- [Strawberry GraphQL](https://strawberry.rocks/) - GraphQL in Python
- [Pydantic](https://docs.pydantic.dev/) - Data validation

### Database Documentation
- [PostgreSQL](https://www.postgresql.org/docs/) - Advanced SQL database
- [MySQL](https://dev.mysql.com/doc/) - Popular SQL database
- [MongoDB](https://docs.mongodb.com/) - NoSQL document database
- [SQLite](https://www.sqlite.org/docs.html) - Lightweight SQL database

### Authentication & Security
- [JWT.io](https://jwt.io/) - JSON Web Tokens
- [OWASP](https://owasp.org/) - Web Security
- [password-validator](https://github.com/dchest/passwords) - Password best practices

## FAQ

**Q: Which database should I use?**
A: See [Database Configuration](DATABASE.md) for comparison. Local development: SQLite. Production: PostgreSQL or MySQL. Flexible schemas: MongoDB.

**Q: How do I add authentication?**
A: Follow [Middleware & Authentication](MIDDLEWARE.md). Simple JWT example included.

**Q: How do I test my code?**
A: See [Development Guide](DEVELOPMENT.md#testing) for testing procedures.

**Q: Can I use both REST and GraphQL?**
A: Yes! Both work together. See [GraphQL Guide](GRAPHQL.md).

**Q: How do I deploy to production?**
A: See "Production best practices" in [Database Configuration](DATABASE.md) and [Development Guide](DEVELOPMENT.md).

## Support

- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions on GitHub Discussions
- **Docs**: Found an error? Submit a PR!

## Contributing

Want to improve Guaro? See [Development Guide](DEVELOPMENT.md#contributing) for contribution guidelines.

---

**Found a doc missing?** Check the main [README](../README.md) or open an issue!
