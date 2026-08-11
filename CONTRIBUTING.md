# Contributing to Loki Middleware / Guide de contribution

[🇫🇷 Version française](#-guide-de-contribution-français) | [🇬🇧 English version](#-contributing-guide-english)

---

## 🇬🇧 Contributing Guide (English)

Thank you for your interest in contributing to **Loki Middleware**. This is an open-source project, and all contributions are welcome: bug fixes, new features, and documentation improvements.

This document provides guidelines and conventions to help you get started quickly.

### 🛠️ Tech Stack & Prerequisites

The project relies on modern tools from the Python ecosystem:

- **Package & dependency manager:** [uv](https://github.com/astral-sh/uv)
- **Linter & formatter:** [Ruff](https://github.com/astral-sh/ruff)
- **Testing framework:** [Pytest](https://docs.pytest.org/)
- **Version & commit management:** [Commitizen](https://commitizen-tools.github.io/commitizen/) (Conventional Commits)

### 🚀 Local Development Environment

#### 1. Clone the repository and install dependencies

```bash
# Clone the repository
git clone https://github.com/IlemLembo/loki-middleware.git
cd loki-middleware

# Sync the virtual environment and install all dependencies, including dev dependencies
uv sync --dev
```

#### 2. Run tests and linting

Before writing code or submitting changes, make sure all local checks pass:

```bash
# Run unit tests
uv run pytest

# Check formatting and linting
uv run ruff check .
uv run ruff format --check .
```

### 📝 Commit Standards (Conventional Commits)

We use Conventional Commits to automate `CHANGELOG.md` generation and semantic versioning (SemVer).

Every commit message must follow this format:

```text
<type>(<optional scope>): <short description in imperative mood>
```

Primary types:

- `feat`: New feature (increments MINOR version)
- `fix`: Bug fix (increments PATCH version)
- `docs`: Documentation updates
- `refactor`: Code refactoring without behavioral changes
- `test`: Adding or updating tests
- `ci`: Continuous integration updates (GitHub Actions)

💡 Tip: You can use the interactive CLI assistant to create formatted commits:

```bash
uv run cz commit
```

### 🔄 Git Workflow

1. **Create a dedicated branch**

	```bash
	git checkout -b feat/add-request-id-header
	# or
	git checkout -b fix/loki-timeout-issue
	```

2. **Develop and test**

	Add unit tests to cover your changes.

3. **Format the code**

	```bash
	uv run ruff format .
	uv run ruff check --fix .
	```

4. **Commit your changes**

	Follow the Conventional Commits rules.

5. **Submit a pull request**

	Push your branch to GitHub and open a PR against the `main` branch.

### 🔒 Security & Reporting

If you discover a security vulnerability, please do not open a public issue. Contact the maintainers directly or use the Security tab on the GitHub repository.

---

## 🇫🇷 Guide de contribution (français)

Merci de votre intérêt pour la contribution à **Loki Middleware**. Ce projet est open source, et toutes les contributions sont les bienvenues : correctifs de bugs, nouvelles fonctionnalités et améliorations de la documentation.

Ce document fournit des directives et des conventions pour vous aider à démarrer rapidement.

### 🛠️ Stack technique et prérequis

Le projet s'appuie sur des outils modernes de l'écosystème Python :

- **Gestionnaire de projet et dépendances :** [uv](https://github.com/astral-sh/uv)
- **Linter et formateur :** [Ruff](https://github.com/astral-sh/ruff)
- **Framework de test :** [Pytest](https://docs.pytest.org/)
- **Gestion des versions et des commits :** [Commitizen](https://commitizen-tools.github.io/commitizen/) (Conventional Commits)

### 🚀 Environnement de développement local

#### 1. Cloner le projet et installer les dépendances

```bash
# Cloner le dépôt
git clone https://github.com/IlemLembo/loki-middleware.git
cd loki-middleware

# Synchroniser l'environnement virtuel et installer toutes les dépendances, y compris celles de développement
uv sync --dev
```

#### 2. Lancer les tests et le linter

Avant d'écrire du code ou de soumettre des modifications, assurez-vous que les contrôles locaux passent :

```bash
# Exécuter les tests unitaires
uv run pytest

# Vérifier le formatage et le linting
uv run ruff check .
uv run ruff format --check .
```

### 📝 Normes de commits (Conventional Commits)

Nous utilisons Conventional Commits pour automatiser la génération du `CHANGELOG.md` et la gestion du versionnement sémantique (SemVer).

Chaque message de commit doit respecter ce format :

```text
<type>(<scope optionnel>): <description courte à l'impératif>
```

Types principaux :

- `feat` : nouvelle fonctionnalité (incrémente la version MINOR)
- `fix` : correction de bug (incrémente la version PATCH)
- `docs` : modification de la documentation
- `refactor` : modification du code sans changement de comportement
- `test` : ajout ou correction de tests
- `ci` : modifications de l'intégration continue (GitHub Actions)

💡 Astuce : vous pouvez utiliser l'assistant CLI interactif pour créer des commits formatés :

```bash
uv run cz commit
```

### 🔄 Flux de travail Git

1. **Créer une branche dédiée**

	```bash
	git checkout -b feat/ajout-header-request-id
	# ou
	git checkout -b fix/correction-timeout-loki
	```

2. **Développer et tester**

	Ajoutez des tests unitaires pour couvrir vos changements.

3. **Formater le code**

	```bash
	uv run ruff format .
	uv run ruff check --fix .
	```

4. **Committer vos changements**

	Respectez les règles des Conventional Commits.

5. **Soumettre une pull request**

	Poussez votre branche sur GitHub et ouvrez une PR vers la branche `main`.

### 🔒 Sécurité et signalement

Si vous découvrez une vulnérabilité de sécurité, merci de ne pas créer d'issue publique. Veuillez contacter directement les mainteneurs ou utiliser l'onglet Security du dépôt GitHub.