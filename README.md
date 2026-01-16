# launchpad

Spec-driven monorepo for rapid service building.

FastCampus Builderthon 2026  
Codename: **DdangHa**  
by **땅콩맛 하쿠 팀**

---

## Overview

`launchpad` is a reusable monorepo template designed for:

- Rapid development in short-term competitions (e.g. builderthon, hackathon)
- Long-term reuse as a personal/team baseline
- AI-assisted, spec-driven development
- Low-cost, scalable infrastructure (serverless-first)

This repository is **not tied to a specific service idea**.

---

## Core Principles

- **Spec First**
  - Specs are written before implementation
  - Code must follow the specs in `/docs/specs`

- **Simple by Default**
  - Avoid premature abstraction
  - One domain = one clear responsibility

- **Builderthon-friendly**
  - Fast local development
  - Minimal infra setup
  - Easy onboarding for junior teammates

---

## Tech Stack (Initial)

### Backend
- FastAPI
- AWS Lambda + API Gateway (planned)
- Railway (DB)
- In-memory / optional cache abstraction

### Frontend
- React + TypeScript
- Feature-Sliced Design (FSD)

### Infra & Tooling
- Docker (local development)
- GitHub Actions (CI)
- Monorepo (pnpm)

---

## Project Structure

```text
apps/        # runnable applications
packages/    # shared code
docs/        # specs & architecture
infra/       # infrastructure-related files
````

---

## How to Start

> Detailed instructions are in `DevelopmentGuide.md`

1. Read the specs in `/docs/specs`
2. Follow the rules defined in `DevelopmentGuide.md`
3. Implement features based on specs

---

## Codename: DdangHa

`DdangHa` is the internal codename for this project.

* Used as a prefix for services, resources, and internal naming
* Represents the team identity of **땅콩맛 하쿠**

---

## License

MIT


