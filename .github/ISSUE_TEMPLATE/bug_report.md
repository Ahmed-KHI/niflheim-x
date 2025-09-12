---
name: Bug Report
about: Create a report to help us improve Niflheim-X
title: '[BUG] '
labels: ['bug']
assignees: ['Ahmed-KHI']

---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce
Steps to reproduce the behavior:
1. Create agent with '...'
2. Call method '...'
3. See error

## 📋 Expected Behavior
A clear and concise description of what you expected to happen.

## 📊 Actual Behavior
A clear and concise description of what actually happened.

## 💻 Environment
- **OS**: [e.g. Windows 11, Ubuntu 22.04, macOS 13]
- **Python Version**: [e.g. 3.10.5]
- **Niflheim-X Version**: [e.g. 0.1.0]
- **LLM Provider**: [e.g. OpenAI, Anthropic]

## 📝 Code Sample
```python
# Minimal code sample that reproduces the issue
from niflheim_x import Agent, OpenAIAdapter

agent = Agent(
    llm=OpenAIAdapter(api_key="test"),
    # ... your configuration
)

# Code that causes the bug
```

## 📋 Error Logs
```
Paste any error messages or logs here
```

## 🔍 Additional Context
Add any other context about the problem here, such as:
- Screenshots (if applicable)
- Related issues
- Potential solutions you've tried