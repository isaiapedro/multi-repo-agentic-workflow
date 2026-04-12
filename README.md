# Portfolio Manager 📁
### (Python, LLMs, GitHub API)

## Contents

- [Introduction](#introduction)
- [How to Run](#how-to-run)
- [Architecture](#architecture)
- [Improvements](#improvements)
- [Conclusion](#conclusion)

## Introduction

Portfolio Manager is a Python package designed for managing portfolios of projects and automating documentation. It leverages AI-powered language models and the GitHub API to gather repository context, manage project metadata, and generate comprehensive, context-aware README files automatically.

## How to Run

1. Initialize a portfolio and add projects
```python
from portfolio import Portfolio
from project import Project

# Create a new portfolio
portfolio = Portfolio()

# Add a project to the portfolio
project = Project(name="My Project", url="[https://example.com](https://example.com)")
portfolio.add_project(project)
```
2. Gather repository context from GitHub
```
from repo_context import gather_repository_context

# Gather repository context information (description, language, topics, etc.)
context = gather_repository_context(repo)
```
3. Generate a Markdown README using the LLM
```
from readme_llm import generate_readme_with_escalation

# Generate README with escalation using the gathered context
readme, used_smart = generate_readme_with_escalation(context, repo.full_name)
print(readme)
```
## Architecture

![Diagram](diagram.png)

• **portfolio**: Manages the overall portfolio, including adding and removing projects.

• **project**: Handles individual project data, including metadata and dependencies.

• **readme_llm**: Uses an AI-powered model to generate README files with Markdown syntax. It also includes utility functions like _should_skip_path to handle and skip binary files during generation.

• **repo_context**: Extracts relevant information from GitHub repositories via the GitHub API, such as file contents, descriptions, primary languages, and topics.

• **workflows**: Defines workflows and pipelines to orchestrate the generation process.

## Improvements

• **Code Organization**: Reorganize the code to make it more modular (e.g., creating separate modules for markdown, github, etc.).

• **Error Handling**: Add robust try-except blocks and logging mechanisms to handle exceptions, edge cases, and unexpected inputs gracefully.

• **Performance Optimization**: Optimize computationally expensive functions, such as the language model calls, to improve the overall efficiency of the package.

•**Testing**: Implement a comprehensive testing suite, including unit and integration tests, to ensure the package's stability and reliability.

• **Documentation & Type Hints**: Provide clearer documentation for each module and use type hints to specify expected input types and return values for easier maintenance and code completion.

• **Code Style**: Strictly follow PEP 8 guidelines for code style, indentation, and naming conventions.

## Conclusion

Thanks for reading up until here. I had a ton of fun doing this project and got a lot of useful insights on Python packaging, API integrations, and working with LLMs. If you want to see similar projects, go to my github page. Feel free to reach me on [LinkedIn](https://www.linkedin.com/in/isaiapedro/) or my [Webpage](https://isaiapedro.github.io/).


Bye! 👋
