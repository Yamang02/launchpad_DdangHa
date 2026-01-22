# 아키텍처 개요

본 문서는 **launchpad** 프로젝트  
(Codename: **DdangHa**)의 전체 아키텍처 구조와 설계 의도를 설명한다.

이 아키텍처는 빌더톤과 같은 단기간 개발 환경을 전제로 하되,  
이후에도 재사용 가능한 구조를 목표로 한다.

---

## 설계 목표

- 무박 2일 환경에서도 **빠른 구현과 수정**
- 최소 비용으로 운영 가능한 구조
- 도메인 단위 확장에 유리
- AI 기반 Spec-driven 개발에 적합

---

## 전체 구조 (High-Level)

```text
[ Web / Admin Client ]
          |
          v
     API Gateway
          |
          v
     AWS Lambda
          |
          v
     FastAPI App
          |
          v
   Database (Railway)
````

### 구조적 특징

* 서버리스 기반으로 **인프라 관리 최소화**
* 모든 요청은 HTTP API 중심
* 상태는 외부 저장소(DB)에 위임

---

## Backend 아키텍처

### 기본 스타일

* **경량 헥사고널 아키텍처**
* 레이어는 엄격히 나누되, 과도한 추상화는 지양

핵심 원칙:

* 도메인 로직은 외부 기술에 의존하지 않는다
* 인터페이스는 얇고 명확하게 유지한다

---

### 실제 디렉토리 구조

**레이어별 구조 (Layer-based):**

```text
app/
├── domain/              # 도메인 레이어
│   ├── user/           # User 도메인
│   │   ├── entities.py
│   │   └── repository.py
│   └── auth/           # Auth 도메인
│       ├── entities.py
│       └── repository.py
│
├── application/         # 애플리케이션 레이어
│   ├── user/
│   │   ├── services.py
│   │   └── dtos.py
│   └── auth/
│       ├── services.py
│       └── dtos.py
│
├── infrastructure/      # 인프라스트럭처 레이어
│   ├── user/
│   │   ├── models.py
│   │   └── repository.py
│   └── auth/
│       ├── jwt_handler.py
│       └── repository.py
│
├── interface/          # 인터페이스 레이어
│   └── http/
│       ├── routers/
│       │   ├── user.py
│       │   └── auth.py
│       └── dependencies.py
│
└── shared/            # 공통 모듈
    ├── database.py
    ├── security.py
    ├── exceptions.py
    └── uid.py
```

**구조 선택 이유:**

레이어별 구조를 채택한 이유:
- **레이어별 의존성 관리**: 각 레이어의 책임이 명확히 분리됨
- **아키텍처 문서와 일치**: 개념적 구조와 실제 구조의 일관성
- **레이어별 코드 탐색**: 같은 레이어의 코드를 한 곳에서 찾을 수 있음
- **도메인 간 공유 용이**: 같은 레이어의 다른 도메인 코드 참조가 쉬움

> **참고**: 일부 프로젝트는 도메인별 구조(`user/domain/`, `user/application/`)를 사용하기도 하지만,
> 본 프로젝트는 레이어별 구조를 채택하여 아키텍처 문서와의 일관성을 유지합니다.

---

## Frontend 아키텍처

### 설계 방식

* **Feature-Sliced Design (FSD)** 채택
* 기술 중심이 아닌 **기능 중심 분리**

```text
shared/
entities/
features/
widgets/
pages/
app/
```

### 기대 효과

* 기능 단위 병렬 작업 가능
* 기획 변경 시 영향 범위 최소화
* Admin / User UI 분리 용이

---

## 환경 전략

* 환경 구분:

  * `dev`
  * `main`
* 실결제, 실운영 트래픽은 고려하지 않음
* 모든 외부 연동은 테스트 모드 기준

---

## 관리자 페이지

* 내부 운영 목적
* 기능 구현보다는 **구조와 접근 제어** 위주
* UI/UX 완성도는 우선순위 아님

---

## 정리

이 아키텍처는 “완벽함”보다
**속도, 명확성, 재사용성**을 우선한다.

빌더톤 이후에도 계속 확장하거나
새 프로젝트의 베이스로 활용할 수 있도록 설계되었다
