# Contributing to Loki Middleware

First off, thank you for taking the time to contribute! 🎉 

Loki Middleware aims to make cloud logging and observability with FastAPI (and soon Django) seamless, performant, and securely compliant with PII redaction rules. Contributions from the community are what make open-source amazing.

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## How Can I Contribute?

### 🐛 Reporting Bugs
* Check the [Issue Tracker](https://github.com/IlemLembo/loki_middleware/issues) to ensure the bug hasn't already been reported.
* If it's a new issue, open a new one using the bug report template. 
* **Important:** When pasting log outputs or error traces, ensure you **manually redact any sensitive data or credentials** before hitting submit.

### 💡 Suggesting Enhancements
* We are actively working on expanding ecosystem support (such as Django integration) and adding alert notification channels (Slack, Discord). 
* If you have an idea, open an issue labeled `enhancement` to discuss its design before diving into the code.

### 🛠️ Submitting Pull Requests (PRs)
1. Fork the repository and create your branch from `main`.
2. Ensure your code follows the existing style guidelines (PEP 8).
3. Write/update tests for any new functionality or bug fixes.
4. Ensure all tests pass locally before pushing.
5. Open a PR with a clear description of the changes.

---

## Local Development Setup

To set up a local development environment, follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/IlemLembo/loki_middleware.git](https://github.com/IlemLembo/loki_middleware.git)
cd loki-middleware