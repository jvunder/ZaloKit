# Contributing to ZaloKit

Thank you for your interest in contributing to ZaloKit! We welcome contributions from the community to help make this the best Python SDK for Zalo.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub and include:
1. A clear description of the bug
2. Steps to reproduce the issue
3. Expected behavior vs actual behavior
4. Your environment (OS, Python version, ZaloKit version)

### Suggesting Enhancements

Have an idea for a new feature? Open an issue with the "enhancement" label and describe:
1. The feature you'd like to see
2. Why it would be useful
3. Any implementation ideas you have

### Pull Requests

1. **Fork the repository** and create your branch from `main`.
2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```
3. **Make your changes**. Ensure you follow the existing code style.
4. **Run tests** to ensure your changes don't break anything:
   ```bash
   pytest
   ```
5. **Add new tests** for any new functionality.
6. **Commit your changes** using descriptive commit messages.
7. **Push to your fork** and submit a Pull Request.

## 💻 Development Setup

```bash
# Clone the repo
git clone https://github.com/jvunder/ZaloKit.git
cd ZaloKit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"
```

## 📝 Code Style

- We use `black` for code formatting.
- We use `isort` for import sorting.
- We use `flake8` for linting.
- Type hints are required for all new code.

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.
