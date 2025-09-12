# Security Policy

## 🛡️ Supported Versions

We actively support the following versions of Niflheim-X with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | ✅ Yes            |
| < 0.1   | ❌ No             |

## 🚨 Reporting a Vulnerability

The Niflheim-X team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:
- **Email**: ahmed@khitech.dev
- **Subject**: [SECURITY] Niflheim-X Vulnerability Report

### What to Include

Please include the following information in your report:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if available)
- Your contact information

### Response Timeline

- **Initial Response**: Within 24-48 hours
- **Assessment**: Within 1 week  
- **Fix Development**: Varies based on complexity
- **Disclosure**: After fix is released

## 🔒 Security Considerations

### API Keys and Secrets
- **Never commit API keys** to version control
- Use environment variables for sensitive configuration
- Rotate API keys regularly
- Use least privilege access for LLM API keys

### Code Execution
- Be cautious with the `tool` decorator - validate inputs
- Never use `eval()` or `exec()` with user input
- Sanitize tool function parameters
- Review tool functions for security implications

### Memory Backends
- **SQLite**: File permissions should be restricted
- **Dict**: Memory is cleared on process termination
- **Vector**: Ensure embedding models are trusted

### Input Validation
- Validate all user inputs to agents
- Sanitize prompts and system messages
- Be aware of prompt injection attacks
- Limit message lengths and conversation history

## 🛠️ Security Best Practices

### For Developers
```python
# ✅ Good: Use environment variables
import os
api_key = os.getenv("OPENAI_API_KEY")

# ❌ Bad: Hardcoded secrets
api_key = "sk-..."

# ✅ Good: Validate tool inputs
@agent.tool
def file_reader(filename: str) -> str:
    if not filename.endswith('.txt'):
        raise ValueError("Only .txt files allowed")
    # ... rest of function

# ❌ Bad: No input validation
@agent.tool  
def file_reader(filename: str) -> str:
    return open(filename).read()  # Dangerous!
```

### For Production
- Use HTTPS for all API communications
- Implement rate limiting
- Monitor for unusual usage patterns
- Keep dependencies updated
- Use virtual environments
- Implement proper logging (without secrets)

## 📋 Dependency Security

We regularly monitor our dependencies for known vulnerabilities:
- **Core dependencies**: 3 minimal, well-maintained packages
- **Optional dependencies**: Vetted for security
- **Updates**: Automated dependency updates via Dependabot

## 🔄 Security Updates

Security updates will be:
- Released as patch versions (e.g., 0.1.1 → 0.1.2)
- Documented in CHANGELOG.md
- Announced on GitHub releases
- Tagged with `security` label

## 📞 Contact

For non-security related issues:
- GitHub Issues: https://github.com/Ahmed-KHI/niflheim-x/issues
- General questions: Create a discussion

For security concerns:
- Email: ahmed@khitech.dev (GPG key available on request)

## 🏆 Recognition

We believe in recognizing security researchers who help improve Niflheim-X:
- Public acknowledgment in release notes (if desired)
- Credit in our security advisory
- Invitation to our security researcher program

---

*Last updated: September 12, 2025*