# Guia de Testes - UGC SaaS

Este guia fornece instruções detalhadas para executar todos os tipos de testes da plataforma UGC SaaS, incluindo testes unitários, de integração, end-to-end e de performance.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Configuração do Ambiente de Testes](#configuração-do-ambiente-de-testes)
3. [Testes do Backend](#testes-do-backend)
4. [Testes do Frontend](#testes-do-frontend)
5. [Testes de Integração](#testes-de-integração)
6. [Testes End-to-End](#testes-end-to-end)
7. [Testes de Performance](#testes-de-performance)
8. [Testes de Segurança](#testes-de-segurança)
9. [Cobertura de Código](#cobertura-de-código)
10. [CI/CD e Automação](#cicd-e-automação)

## 🎯 Visão Geral

### Estratégia de Testes
A plataforma UGC SaaS utiliza uma abordagem de testes em pirâmide:

```
        /\
       /  \
      / E2E \     ← Poucos testes, alto valor
     /______\
    /        \
   /Integration\ ← Testes moderados, médio valor
  /__________\
 /            \
/   Unit Tests  \ ← Muitos testes, baixo custo
/________________\
```

### Tipos de Testes
- **Unitários**: Testam componentes isolados
- **Integração**: Testam interação entre componentes
- **End-to-End**: Testam fluxos completos do usuário
- **Performance**: Testam velocidade e escalabilidade
- **Segurança**: Testam vulnerabilidades e autenticação

### Ferramentas Utilizadas
- **Backend**: pytest, pytest-asyncio, httpx
- **Frontend**: Jest, React Testing Library, Cypress
- **API**: Postman, Newman
- **Performance**: Artillery, k6
- **Segurança**: OWASP ZAP, Bandit

## ⚙️ Configuração do Ambiente de Testes

### Pré-requisitos
```bash
# Instalar dependências de teste
cd backend && pip install -r requirements-test.txt
cd frontend && npm install --dev
```

### Variáveis de Ambiente para Testes
```bash
# Criar arquivo .env.test
cp .env.example .env.test

# Configurar para testes
MONGODB_URL=mongodb://localhost:27017/ugc_saas_test
REDIS_URL=redis://localhost:6379/1
OPENAI_API_KEY=test_key
SENDGRID_API_KEY=test_key
```

### Banco de Dados de Teste
```bash
# Iniciar MongoDB para testes
docker run -d --name mongo-test -p 27017:27017 mongo:7.0

# Iniciar Redis para testes
docker run -d --name redis-test -p 6379:6379 redis:7.2-alpine
```

## 🔧 Testes do Backend

### Estrutura de Testes
```
backend/tests/
├── conftest.py              # Configurações pytest
├── test_auth.py            # Testes de autenticação
├── test_profiles.py        # Testes de perfis
├── test_reports.py         # Testes de relatórios
├── test_feedback.py        # Testes de feedback
├── test_instagram.py       # Testes Instagram API
├── test_ai.py             # Testes de IA
└── utils/
    ├── fixtures.py         # Fixtures reutilizáveis
    └── helpers.py          # Funções auxiliares
```

### Configuração do pytest
```python
# backend/tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.database import get_database
from app.models import UserInDB, ProfileInDB

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_user():
    """Create test user."""
    user_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": "$2b$12$test_hash",
        "is_active": True
    }
    
    db = get_database()
    result = await db.users.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    
    yield UserInDB(**user_data)
    
    # Cleanup
    await db.users.delete_one({"_id": result.inserted_id})

@pytest.fixture
async def auth_headers(test_user):
    """Create authentication headers."""
    from app.auth import create_access_token
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
```

### Testes de Autenticação
```python
# backend/tests/test_auth.py
import pytest
from httpx import AsyncClient

class TestAuth:
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "full_name": "New User",
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user"]["email"] == user_data["email"]
        assert "password" not in data["user"]
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "full_name": "Another User",
            "email": test_user.email,
            "password": "password123"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login."""
        login_data = {
            "email": test_user.email,
            "password": "password123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid credentials" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_user):
        """Test token refresh."""
        from app.auth import create_refresh_token
        
        refresh_token = create_refresh_token(data={"sub": str(test_user.id)})
        
        response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
```

### Testes de Perfis
```python
# backend/tests/test_profiles.py
import pytest
from httpx import AsyncClient

class TestProfiles:
    
    @pytest.mark.asyncio
    async def test_get_profile_success(self, client: AsyncClient, auth_headers, test_profile):
        """Test getting user profile."""
        response = await client.get("/profiles/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_profile.id)
        assert data["display_name"] == test_profile.display_name
    
    @pytest.mark.asyncio
    async def test_update_profile_success(self, client: AsyncClient, auth_headers):
        """Test updating user profile."""
        update_data = {
            "display_name": "Updated Name",
            "bio": "Updated bio",
            "niche": "fashion"
        }
        
        response = await client.put("/profiles/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["profile"]["display_name"] == update_data["display_name"]
    
    @pytest.mark.asyncio
    async def test_get_dashboard_data(self, client: AsyncClient, auth_headers):
        """Test getting dashboard data."""
        response = await client.get("/profiles/me/dashboard", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "profile" in data
        assert "current_metrics" in data
        assert "growth_metrics" in data
```

### Executar Testes do Backend
```bash
# Todos os testes
cd backend && python -m pytest

# Testes específicos
python -m pytest tests/test_auth.py

# Com cobertura
python -m pytest --cov=app --cov-report=html

# Testes paralelos
python -m pytest -n auto

# Verbose
python -m pytest -v
```

## 🎨 Testes do Frontend

### Estrutura de Testes
```
frontend/src/
├── __tests__/              # Testes unitários
│   ├── components/         # Testes de componentes
│   ├── pages/             # Testes de páginas
│   ├── contexts/          # Testes de contextos
│   └── utils/             # Testes de utilitários
├── cypress/               # Testes E2E
│   ├── e2e/              # Specs E2E
│   ├── fixtures/         # Dados de teste
│   └── support/          # Comandos customizados
└── jest.config.js        # Configuração Jest
```

### Configuração do Jest
```javascript
// frontend/jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/reportWebVitals.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### Testes de Componentes
```javascript
// frontend/src/__tests__/components/Dashboard.test.jsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import Dashboard from '@/pages/Dashboard';

// Mock da API
jest.mock('@/lib/api', () => ({
  get: jest.fn()
}));

const MockedDashboard = () => (
  <BrowserRouter>
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  </BrowserRouter>
);

describe('Dashboard Component', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });

  test('renders dashboard with loading state', () => {
    render(<MockedDashboard />);
    
    expect(screen.getByText(/carregando/i)).toBeInTheDocument();
  });

  test('displays metrics after loading', async () => {
    const mockData = {
      current_metrics: {
        followers_count: 1000,
        posts_count: 50,
        avg_engagement_rate: 4.5
      }
    };

    require('@/lib/api').get.mockResolvedValue({ data: mockData });

    render(<MockedDashboard />);

    await waitFor(() => {
      expect(screen.getByText('1000')).toBeInTheDocument();
      expect(screen.getByText('50')).toBeInTheDocument();
      expect(screen.getByText('4.5%')).toBeInTheDocument();
    });
  });

  test('handles API error gracefully', async () => {
    require('@/lib/api').get.mockRejectedValue(new Error('API Error'));

    render(<MockedDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/erro ao carregar/i)).toBeInTheDocument();
    });
  });
});
```

### Testes de Hooks Customizados
```javascript
// frontend/src/__tests__/hooks/useAuth.test.js
import { renderHook, act } from '@testing-library/react';
import { useAuth } from '@/contexts/AuthContext';
import { AuthProvider } from '@/contexts/AuthContext';

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

describe('useAuth Hook', () => {
  test('initial state is unauthenticated', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.loading).toBe(false);
  });

  test('login updates state correctly', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    const mockUser = { id: '1', email: 'test@example.com' };
    
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });
    
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });
});
```

### Executar Testes do Frontend
```bash
# Todos os testes
cd frontend && npm test

# Testes em modo watch
npm test -- --watch

# Com cobertura
npm test -- --coverage

# Testes específicos
npm test -- Dashboard.test.jsx

# Atualizar snapshots
npm test -- --updateSnapshot
```

## 🔗 Testes de Integração

### Testes de API com Postman
```json
{
  "info": {
    "name": "UGC SaaS API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication Flow",
      "item": [
        {
          "name": "Register User",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"full_name\": \"Test User\",\n  \"email\": \"test@example.com\",\n  \"password\": \"password123\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/register",
              "host": ["{{base_url}}"],
              "path": ["auth", "register"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status code is 201', function () {",
                  "    pm.response.to.have.status(201);",
                  "});",
                  "",
                  "pm.test('Response has user data', function () {",
                  "    const jsonData = pm.response.json();",
                  "    pm.expect(jsonData).to.have.property('user');",
                  "    pm.expect(jsonData.user).to.have.property('email');",
                  "});"
                ]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Executar Testes com Newman
```bash
# Instalar Newman
npm install -g newman

# Executar collection
newman run postman_collection.json -e environment.json

# Com relatório HTML
newman run postman_collection.json -e environment.json -r html
```

### Testes de Integração com Docker
```python
# backend/tests/test_integration.py
import pytest
import docker
from httpx import AsyncClient

@pytest.fixture(scope="session")
def docker_services():
    """Start Docker services for integration tests."""
    client = docker.from_env()
    
    # Start MongoDB
    mongo_container = client.containers.run(
        "mongo:7.0",
        ports={'27017/tcp': 27017},
        detach=True,
        remove=True
    )
    
    # Start Redis
    redis_container = client.containers.run(
        "redis:7.2-alpine",
        ports={'6379/tcp': 6379},
        detach=True,
        remove=True
    )
    
    yield
    
    # Cleanup
    mongo_container.stop()
    redis_container.stop()

@pytest.mark.integration
class TestFullFlow:
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self, docker_services):
        """Test complete user journey from registration to report generation."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. Register user
            register_response = await client.post("/auth/register", json={
                "full_name": "Integration Test User",
                "email": "integration@example.com",
                "password": "password123"
            })
            assert register_response.status_code == 201
            
            # 2. Login
            login_response = await client.post("/auth/login", json={
                "email": "integration@example.com",
                "password": "password123"
            })
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3. Update profile
            profile_response = await client.put("/profiles/me", json={
                "display_name": "Integration User",
                "niche": "lifestyle"
            }, headers=headers)
            assert profile_response.status_code == 200
            
            # 4. Generate report
            report_response = await client.post("/reports/generate", json={
                "title": "Test Report",
                "report_type": "custom"
            }, headers=headers)
            assert report_response.status_code == 202
```

## 🎭 Testes End-to-End

### Configuração do Cypress
```javascript
// frontend/cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.js',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    env: {
      apiUrl: 'http://localhost:8000'
    }
  }
});
```

### Comandos Customizados
```javascript
// frontend/cypress/support/commands.js
Cypress.Commands.add('login', (email, password) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    body: { email, password }
  }).then((response) => {
    window.localStorage.setItem('access_token', response.body.access_token);
  });
});

Cypress.Commands.add('createTestUser', () => {
  const user = {
    full_name: 'Cypress Test User',
    email: `test-${Date.now()}@example.com`,
    password: 'password123'
  };
  
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/register`,
    body: user
  }).then(() => user);
});
```

### Testes E2E
```javascript
// frontend/cypress/e2e/user-journey.cy.js
describe('Complete User Journey', () => {
  let testUser;
  
  beforeEach(() => {
    cy.createTestUser().then((user) => {
      testUser = user;
    });
  });
  
  it('should complete full user registration and setup flow', () => {
    // Visit homepage
    cy.visit('/');
    
    // Navigate to register
    cy.get('[data-cy=register-link]').click();
    
    // Fill registration form
    cy.get('[data-cy=full-name-input]').type(testUser.full_name);
    cy.get('[data-cy=email-input]').type(testUser.email);
    cy.get('[data-cy=password-input]').type(testUser.password);
    cy.get('[data-cy=register-button]').click();
    
    // Should redirect to login
    cy.url().should('include', '/login');
    cy.get('[data-cy=success-message]').should('contain', 'Registration successful');
    
    // Login
    cy.get('[data-cy=email-input]').type(testUser.email);
    cy.get('[data-cy=password-input]').type(testUser.password);
    cy.get('[data-cy=login-button]').click();
    
    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.get('[data-cy=welcome-message]').should('contain', testUser.full_name);
    
    // Navigate to profile setup
    cy.get('[data-cy=profile-menu]').click();
    cy.get('[data-cy=profile-link]').click();
    
    // Fill profile form
    cy.get('[data-cy=display-name-input]').type('Cypress Test Creator');
    cy.get('[data-cy=bio-input]').type('Test bio for Cypress');
    cy.get('[data-cy=niche-select]').select('lifestyle');
    cy.get('[data-cy=save-profile-button]').click();
    
    // Verify profile saved
    cy.get('[data-cy=success-message]').should('contain', 'Profile updated');
    
    // Navigate to reports
    cy.get('[data-cy=reports-link]').click();
    cy.url().should('include', '/reports');
    
    // Generate custom report
    cy.get('[data-cy=generate-report-button]').click();
    cy.get('[data-cy=report-title-input]').type('Cypress Test Report');
    cy.get('[data-cy=report-type-select]').select('custom');
    cy.get('[data-cy=create-report-button]').click();
    
    // Verify report creation started
    cy.get('[data-cy=success-message]').should('contain', 'Report generation started');
  });
  
  it('should handle Instagram connection flow', () => {
    cy.login(testUser.email, testUser.password);
    cy.visit('/profile');
    
    // Click connect Instagram
    cy.get('[data-cy=connect-instagram-button]').click();
    
    // Should open Instagram auth (we'll mock this)
    cy.window().its('open').should('have.been.called');
    
    // Simulate successful connection
    cy.window().then((win) => {
      win.postMessage({
        type: 'INSTAGRAM_AUTH_SUCCESS',
        data: { code: 'test_code', state: 'test_state' }
      }, '*');
    });
    
    // Verify connection status
    cy.get('[data-cy=instagram-status]').should('contain', 'Connected');
  });
});
```

### Executar Testes E2E
```bash
# Interface gráfica
cd frontend && npx cypress open

# Modo headless
npx cypress run

# Testes específicos
npx cypress run --spec "cypress/e2e/user-journey.cy.js"

# Com gravação de vídeo
npx cypress run --record --key <record_key>
```

## ⚡ Testes de Performance

### Configuração do Artillery
```yaml
# performance/load-test.yml
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 120
      arrivalRate: 50
      name: "Load test"
    - duration: 60
      arrivalRate: 100
      name: "Stress test"
  payload:
    path: "users.csv"
    fields:
      - "email"
      - "password"

scenarios:
  - name: "Authentication Flow"
    weight: 30
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.access_token"
              as: "token"
      - get:
          url: "/profiles/me"
          headers:
            Authorization: "Bearer {{ token }}"

  - name: "Dashboard Load"
    weight: 50
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.access_token"
              as: "token"
      - get:
          url: "/profiles/me/dashboard"
          headers:
            Authorization: "Bearer {{ token }}"

  - name: "Report Generation"
    weight: 20
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.access_token"
              as: "token"
      - post:
          url: "/reports/generate"
          headers:
            Authorization: "Bearer {{ token }}"
          json:
            title: "Load Test Report"
            report_type: "weekly"
```

### Executar Testes de Performance
```bash
# Instalar Artillery
npm install -g artillery

# Executar teste de carga
artillery run performance/load-test.yml

# Com relatório HTML
artillery run performance/load-test.yml --output report.json
artillery report report.json
```

### Testes com k6
```javascript
// performance/k6-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(99)<1500'],
    http_req_failed: ['rate<0.1'],
  },
};

export default function () {
  // Login
  let loginResponse = http.post('http://localhost:8000/auth/login', {
    email: 'test@example.com',
    password: 'password123'
  });
  
  check(loginResponse, {
    'login status is 200': (r) => r.status === 200,
    'login response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  if (loginResponse.status === 200) {
    let token = loginResponse.json('access_token');
    
    // Get dashboard
    let dashboardResponse = http.get('http://localhost:8000/profiles/me/dashboard', {
      headers: { Authorization: `Bearer ${token}` },
    });
    
    check(dashboardResponse, {
      'dashboard status is 200': (r) => r.status === 200,
      'dashboard response time < 1000ms': (r) => r.timings.duration < 1000,
    });
  }
  
  sleep(1);
}
```

## 🔒 Testes de Segurança

### Testes com Bandit (Python)
```bash
# Instalar Bandit
pip install bandit

# Executar análise de segurança
cd backend && bandit -r app/

# Com relatório JSON
bandit -r app/ -f json -o security-report.json
```

### Testes com OWASP ZAP
```bash
# Executar ZAP em modo daemon
docker run -u zap -p 8080:8080 -i owasp/zap2docker-stable zap.sh -daemon -host 0.0.0.0 -port 8080

# Executar baseline scan
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:3000
```

### Testes de Autenticação
```python
# backend/tests/test_security.py
import pytest
from httpx import AsyncClient

class TestSecurity:
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test that protected endpoints require authentication."""
        response = await client.get("/profiles/me")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_token(self, client: AsyncClient):
        """Test that invalid tokens are rejected."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/profiles/me", headers=headers)
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, client: AsyncClient):
        """Test protection against SQL injection."""
        malicious_input = "'; DROP TABLE users; --"
        response = await client.post("/auth/login", json={
            "email": malicious_input,
            "password": "password"
        })
        # Should not crash the server
        assert response.status_code in [400, 401]
    
    @pytest.mark.asyncio
    async def test_xss_protection(self, client: AsyncClient, auth_headers):
        """Test protection against XSS attacks."""
        malicious_script = "<script>alert('xss')</script>"
        response = await client.put("/profiles/me", json={
            "display_name": malicious_script
        }, headers=auth_headers)
        
        # Should sanitize input
        assert response.status_code == 200
        data = response.json()
        assert "<script>" not in data["profile"]["display_name"]
```

## 📊 Cobertura de Código

### Backend (Python)
```bash
# Executar com cobertura
cd backend && python -m pytest --cov=app --cov-report=html --cov-report=term

# Verificar cobertura mínima
python -m pytest --cov=app --cov-fail-under=80
```

### Frontend (JavaScript)
```bash
# Executar com cobertura
cd frontend && npm test -- --coverage --watchAll=false

# Configurar threshold no package.json
{
  "jest": {
    "collectCoverageFrom": [
      "src/**/*.{js,jsx}",
      "!src/index.js"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

### Relatórios de Cobertura
```bash
# Gerar relatório combinado
mkdir -p coverage/combined
cp backend/htmlcov/* coverage/combined/backend/
cp frontend/coverage/lcov-report/* coverage/combined/frontend/
```

## 🚀 CI/CD e Automação

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:7.0
        ports:
          - 27017:27017
      redis:
        image: redis:7.2-alpine
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        cd backend
        python -m pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Start services
      run: |
        docker-compose up -d
        sleep 30
    
    - name: Run E2E tests
      uses: cypress-io/github-action@v5
      with:
        working-directory: frontend
        wait-on: 'http://localhost:3000'
        wait-on-timeout: 120
    
    - name: Upload screenshots
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: cypress-screenshots
        path: frontend/cypress/screenshots
```

### Scripts de Automação
```bash
#!/bin/bash
# scripts/run-all-tests.sh

set -e

echo "🧪 Running all tests..."

# Backend tests
echo "🔧 Running backend tests..."
cd backend
python -m pytest --cov=app --cov-report=term --cov-report=html
cd ..

# Frontend tests
echo "🎨 Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
cd ..

# Integration tests
echo "🔗 Running integration tests..."
docker-compose -f docker-compose.test.yml up -d
sleep 30
newman run postman_collection.json -e test_environment.json
docker-compose -f docker-compose.test.yml down

# E2E tests
echo "🎭 Running E2E tests..."
cd frontend
npx cypress run
cd ..

# Performance tests
echo "⚡ Running performance tests..."
artillery run performance/load-test.yml

echo "✅ All tests completed successfully!"
```

### Makefile para Testes
```makefile
# Makefile
.PHONY: test test-backend test-frontend test-e2e test-integration test-performance

test: test-backend test-frontend test-integration test-e2e
	@echo "✅ All tests passed!"

test-backend:
	@echo "🔧 Running backend tests..."
	cd backend && python -m pytest --cov=app

test-frontend:
	@echo "🎨 Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false

test-integration:
	@echo "🔗 Running integration tests..."
	docker-compose -f docker-compose.test.yml up -d
	sleep 30
	newman run postman_collection.json -e test_environment.json
	docker-compose -f docker-compose.test.yml down

test-e2e:
	@echo "🎭 Running E2E tests..."
	cd frontend && npx cypress run

test-performance:
	@echo "⚡ Running performance tests..."
	artillery run performance/load-test.yml

test-security:
	@echo "🔒 Running security tests..."
	cd backend && bandit -r app/
	docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:3000

coverage:
	@echo "📊 Generating coverage report..."
	cd backend && python -m pytest --cov=app --cov-report=html
	cd frontend && npm test -- --coverage --watchAll=false
	@echo "Coverage reports generated in backend/htmlcov and frontend/coverage"
```

---

**Este guia de testes deve ser seguido para garantir a qualidade e confiabilidade da plataforma UGC SaaS. Mantenha os testes atualizados conforme novas funcionalidades são adicionadas.**

