# Runner Linting Process Documentation

## Overview

Most of the linting is done by MegaLinter, it is a static analysis tool that runs multiple linters and formatters on different file types in the repository. It's designed to maintain code quality and consistency across the entire codebase by checking different file types with appropriate linters. Python linting is treated separately which will be explained in this doc.

- **Tool**: [MegaLinter](https://megalinter.io/)
- **Docker Image**: `ghcr.io/oxsecurity/megalinter:vX.X.X`
- **Repository**: https://github.com/oxsecurity/megalinter

## Linting Summary Table

| Filetype           | Linter                    | Config File                               | Ignore Files                                     |
|--------------------|---------------------------|-------------------------------------------|--------------------------------------------------|
| JavaScript/JSON    | ESLint v9                 | `eslint.config.js`                        | `eslint.config.js`, `.prettierignore`            |
| Python             | ruff, pylint, mypy, black | `pyproject.toml`, `.pylintrc`, `mypy.ini` | `.pylintrc`, `setup.cfg`                         |
| HTML               | djLint                    | `pyproject.toml`                          | `pyproject.toml`                                 |
| JSON               | jsonlint                  | `.mega-linter.yml`                        | (none)                                           |
| Markdown           | markdownlint              | `.mega-linter.yml`                        | `.markdownlintignore`                            |
| YAML               | yamllint                  | `.mega-linter.yml`                        | (none)                                           |
| All Files          | editorconfig-checker      | `.editorconfig`                           | (none)                                           |
| GitHub Actions     | Zizmor                    | `.mega-linter.yml`                        | (none)                                           |
| Dockerfile         | hadolint                  | `.mega-linter.yml`                        | `.dockerignore`                                  |

## How to Run MegaLinter

### Prerequisites
- Docker installed and running

### Local Execution

#### Check for Issues (Report Only)
```bash
make megalint
```
- Runs all enabled linters
- Reports issues but does not modify files
- Output saved to `megalinter-reports/` directory

#### Fix Issues Automatically
```bash
make megalint-apply
```
- Runs all enabled linters with auto-fix enabled
- Automatically fixes issues where possible
- Some issues may still require manual intervention
- Sets `APPLY_FIXES=all` environment variable

#### Clean Up Reports
```bash
make clean-megalint
```
- Deletes the `megalinter-reports/` directory
- Use before re-running to get fresh results

### CI/CD Execution (GitHub Actions)

MegaLinter runs automatically on every pull request to `main` via the GitHub Actions workflow:

**Workflow File**: [.github/workflows/mega-linter.yml](.github/workflows/mega-linter.yml)

**Process**:
1. Triggered on pull request to `main` branch
2. Checks out code using GitHub token
3. Runs MegaLinter via Docker
4. Reports results (status reports disabled, comment reports disabled)
5. PR fails if linting errors detected

**To Skip CI Failures**: Fix all MegaLinter issues locally using `make megalint-apply`, then push changes.

### Report Location
- **Directory**: `megalinter-reports/` (generated in repository root)

## Global Excludes (Applied by MegaLinter)
- Typically excludes: `.git`, `.venv`, `node_modules`, etc.

## Configuration Location

### Primary Configuration File
- **File**: [.mega-linter.yml](.mega-linter.yml) (repository root)
- **Reference**: https://megalinter.io/latest/config-file/

### CI/CD Integration
- **GitHub Actions Workflow**: [.github/workflows/mega-linter.yml](.github/workflows/mega-linter.yml)
- **Trigger**: Pull requests to `main` branch
- **Status Reporters**: Disabled (GITHUB_STATUS_REPORTER: false, GITHUB_COMMENT_REPORTER: false)

## Enabled Linters by Filetype

The following linters are enabled in `.mega-linter.yml`:

### 1. **JAVASCRIPT** (JavaScript/TypeScript Code)
- **Linter**: ESLint
- **Filetypes**: `.js`, `.json` files (in test directories and config files)
- **Purpose**: Lint JavaScript test files and validate JavaScript-related JSON configurations
- **Special Configuration**:
  ```yaml
  JAVASCRIPT_ES_CLI_EXECUTABLE:
    - node_modules/.bin/eslint

  JAVASCRIPT_ES_PRE_COMMANDS:
    - command: npm ci --include=dev
      cwd: workspace
  ```
  - Forces use of local ESLint v9 binary (not MegaLinter's default v10)
  - Runs `npm ci --include=dev` before linting to ensure devDependencies are installed
  - **Why**: ESLint v10 has compatibility issues with current dependencies
- **ESLint Configuration**: [eslint.config.js](../eslint.config.js)
  - Uses `neostandard` for base rules
  - ES11 target with custom rules for the codebase
  - Requires double quotes, semicolons, 2-space indentation
- **Disabled Variant**: `JAVASCRIPT_STANDARD` (conflicting rules with ESLint configuration)

### 2. **ACTION** (GitHub Actions Workflows)
- **Linter**: Zizmor
- **Filetypes**: `.yml`, `.yaml` files in `.github/workflows/` directory
- **Purpose**: Check for security issues and best practices in GitHub Actions workflows
- **Special Configuration**:
  ```yaml
  ACTION_ZIZMOR_UNSECURED_ENV_VARIABLES:
    - GITHUB_TOKEN
  ```
  - Flags usage of `GITHUB_TOKEN` in workflow environment variables as a security concern

### 2. **DOCKERFILE**
- **Filetypes**: Dockerfile, `.dockerfile` files
- **Purpose**: Lint Docker configuration files for best practices

### 3. **EDITORCONFIG**
- **Filetypes**: All files (validated against `.editorconfig` rules)
- **Purpose**: Ensure file formatting consistency (line endings, indentation, etc.)

### 4. **HTML**
- **Linter**: djLint
- **Filetypes**: `.html` files
- **Purpose**: Lint HTML templates with Jinja2 support
- **Special Configuration**:
  ```yaml
  HTML_DJLINT_ARGUMENTS: ["--profile", "jinja"]
  ```
  - Configured to recognise and accept Jinja2 template syntax
  - This project uses Jinja2 for server-side templating
- **Disabled Linter**: `HTML_HTMLHINT`
  - **Reason**: HTMLHint doesn't understand Jinja2 syntax, causing false positives

### 5. **JSON**
- **Filetypes**: `.json` files
- **Purpose**: Validate JSON file syntax and formatting

### 6. **MARKDOWN**
- **Filetypes**: `.md` files
- **Purpose**: Lint Markdown documentation files

### 7. **YAML**
- **Filetypes**: `.yml`, `.yaml` files
- **Purpose**: Validate YAML file syntax and best practices

### Python Linting (non MegaLinter)

**PYTHON**
- **Reason**: Intentionally disabled per ONS Python template recommendation
- **Rationale**: Python linting is handled separately from MegaLinter
- **Alternative**: Python-specific linting script [scripts/run_lint_python.sh](../scripts/run_lint_python.sh)
  - Uses: ruff, pylint, mypy, black
  - Excludes: `node_modules|megalinter-reports`

## Configuration Settings

### Global Settings (in `.mega-linter.yml`)

```yaml
FORMATTERS_DISABLE_ERRORS: false
```
- If a formatter (auto-fixer) encounters an error, the linting will fail
- Ensures code is actually fixable when using `make megalint-apply`

```yaml
SHOW_ELAPSED_TIME: true
```
- Displays execution time for each linter
- Useful for performance monitoring

```yaml
FLAVOR_SUGGESTIONS: false
```
- Disables suggestions to use different MegaLinter flavors
- Reduces noise in output

### JavaScript-Specific Configuration

**ESLint v9 vs v10 Compatibility Issue**

MegaLinter v9 uses ESLint v10 by default, but this project is locked to ESLint v9 due to dependency compatibility issues:

**Dependencies requiring ESLint v9:**
- `neostandard` v0.13.0 requires `eslint@^9.0.0` (no v10 support)
- `eslint-plugin-import` v2.32.0 requires `eslint@^9` (no v10 support)
- `eslint-plugin-promise` v6.6.0 requires `eslint@^9` (no v10 support)

**Workaround in `.mega-linter.yml`:**
```yaml
JAVASCRIPT_ES_CLI_EXECUTABLE:
  - node_modules/.bin/eslint

JAVASCRIPT_ES_PRE_COMMANDS:
  - command: npm ci --include=dev
    cwd: workspace
```

- Forces MegaLinter to use the local ESLint v9 binary from `node_modules/`
- Runs `npm ci --include=dev` as a pre-command to ensure dependencies are installed
- In GitHub Actions, this is necessary because `node_modules/` may not exist initially

**Status**: Awaiting ESLint 10 support in `neostandard` before upgrading. See [/memories/repo/eslint-10-blocker.md](/memories/repo/eslint-10-blocker.md) for details.
