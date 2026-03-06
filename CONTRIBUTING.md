# Contributing to Document OCR Verification System

First off, thank you for considering contributing to the Document OCR Verification System! It's people like you that make this project such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [I don't want to read this whole thing, I just have a question!](#i-dont-want-to-read-this-whole-thing-i-just-have-a-question)
- [What should I know before I get started?](#what-should-i-know-before-i-get-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Styleguides](#styleguides)
- [Additional Notes](#additional-notes)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the maintainers.

## I don't want to read this whole thing, I just have a question!

- **Have a question about how to use the system?** → Check the [README](README.md) and [API Documentation](README.md#-api-documentation)
- **Found a bug?** → Open an [Issue](https://github.com/devejya56/document-ocr-verification-system/issues)
- **Feature suggestion?** → Open a [Discussion](https://github.com/devejya56/document-ocr-verification-system/discussions)

## What should I know before I get started?

### Project Structure

The project follows this structure:

```
backend/
├── __init__.py           # Package initialization
├── main.py               # FastAPI application
├── models.py             # Pydantic data models
├── ocr_engine.py         # OCR processing logic
└── verification.py       # Verification logic
```

### Technology Stack

- **Framework**: FastAPI
- **Web Server**: Uvicorn
- **OCR Engine**: EasyOCR
- **Data Validation**: Pydantic
- **Python Version**: 3.8+

### Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Install development dependencies: `pip install pytest black pylint`
5. Run the application: `uvicorn backend.main:app --reload`

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps which reproduce the problem**
- **Provide specific examples to demonstrate those steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots or animated GIFs if possible**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/devejya56/document-ocr-verification-system/issues). When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

Please follow these steps to contribute code:

1. **Fork the repository** and create your branch from `main`
   ```bash
   git clone https://github.com/yourusername/document-ocr-verification-system.git
   cd document-ocr-verification-system
   git checkout -b feature/my-feature
   ```

2. **Make your changes**
   - Follow the [Styleguides](#styleguides)
   - Add or update tests as appropriate
   - Update documentation if needed

3. **Test your changes**
   ```bash
   # Run tests
   pytest tests/ -v
   
   # Check code style
   pylint backend/
   
   # Format code
   black backend/
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   git push origin feature/my-feature
   ```

5. **Create a Pull Request**
   - Fill in the PR template with clear description
   - Link related issues using `Closes #issue-number`
   - Ensure all CI checks pass
   - Request review from maintainers

## Styleguides

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for code formatting
- Use [Pylint](https://www.pylint.org/) for code analysis

### Example Python Code

```python
def extract_document_info(document_path: str, document_type: str) -> dict:
    """
    Extract information from a document.
    
    Args:
        document_path: Path to the document file
        document_type: Type of document (e.g., 'passport', 'id')
    
    Returns:
        Dictionary containing extracted information
        
    Raises:
        FileNotFoundError: If document file is not found
        ValueError: If document type is not supported
    """
    # Implementation here
    pass
```

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
- Examples:
  - `Add OCR engine optimization for faster processing`
  - `Fix: Handle empty document gracefully`
  - `Docs: Update API endpoint documentation`
  - `Refactor: Extract field parsing logic`

### Documentation Style

- Write clear, descriptive comments for complex logic
- Use docstrings for all functions and classes
- Update README.md if you change functionality
- Use Markdown for all documentation files

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help track and manage issues and pull requests.

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `question` - Further information is requested
- `wontfix` - This will not be worked on

### Development Workflow

1. Check existing issues and PRs to avoid duplicate work
2. Create an issue for your feature/bug before starting work
3. Keep PRs focused on a single feature or bug fix
4. Write clear commit messages
5. Request reviews when ready
6. Be responsive to feedback

### Testing

- Write tests for new features
- Ensure all tests pass: `pytest tests/ -v`
- Maintain or improve code coverage
- Test edge cases and error conditions

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Update API documentation for endpoint changes
- Include examples in documentation

## Recognition

Contributors will be recognized in:
- The project's contributors page
- Release notes for their contributions
- GitHub's automatic contributor recognition

---

**Thank you for contributing! 🎉**
