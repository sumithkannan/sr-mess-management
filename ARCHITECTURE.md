# SR Mess Management Architecture

```mermaid
flowchart TB
    subgraph CLIENT["1 · Client"]
        direction LR
        Browser["Browser"]
        SPA["Vue 3 SPA<br/>Views · Vue Router · Pinia"]
        Axios["Axios<br/>JWT header · 401 redirects"]
        Browser --> SPA --> Axios
    end

    subgraph HOST["2 · Hosting & transport"]
        direction LR
        Vercel["Vercel<br/>Serves SPA"]
        HTTP["HTTPS API calls<br/>JSON · multipart · files"]
        ASGI["PythonAnywhere / ASGI"]
        CORS["FastAPI CORS"]
        Vercel --> Browser
        Axios --> HTTP --> ASGI --> CORS
    end

    subgraph APP["3 · API & application"]
        direction TB
        FastAPI["FastAPI<br/>Router registration · startup migrations · health"]
        CORS --> FastAPI

        subgraph ENDPOINTS["REST endpoints · method / path · request → response"]
            direction LR
            AUTH["Auth · /api/auth<br/>POST /login · credentials → token + user<br/>GET /me → user<br/>POST /change-password · current + new → message"]
            PEOPLE["Users · /api/users<br/>GET /, /active → users<br/>POST / · user fields → user<br/>PUT /{id} · updates → user<br/>PATCH /{id}/suspend|activate|role → message<br/>DELETE /{id} → message<br/>GET /bulk/template → XLSX · POST /bulk · XLSX → result<br/><br/>Duty · /api/mess-duty<br/>GET /, /current, /on-date/{date} → assignments/users<br/>POST / · user + date range → assignment<br/>PUT /{id} · updates → assignment · DELETE /{id} → message"]
            MEALS["Menu · /api/meal-types, /api/menu-items<br/>GET list/date/recurring → items<br/>POST · item fields → item<br/>PUT /{id} · updates → item<br/>DELETE /{id} → message<br/>POST /generate/{date} → message<br/><br/>Votes · /api/votes<br/>GET /date|my/{date} → votes<br/>POST · item + meal + date → vote<br/>DELETE /{id} → message<br/><br/>Attendance · /api/attendance<br/>GET /date/{date}/{meal} → records<br/>POST · user + meal + date → record<br/>POST /batch · users + meal + date → result<br/>DELETE /{id} → message<br/><br/>Ratings · /api/ratings<br/>GET /date|my/{date} → ratings<br/>POST · item + meal + date + score → rating"]
            ADMIN["Expenses · /api/expenses [admin]<br/>GET /?month&year → expenses<br/>GET /monthly-summary → totals<br/>POST / · expense fields → expense<br/>POST /upload · fields + bill → expense<br/>PUT /{id} · updates → expense<br/>PUT /{id}/upload · fields + optional bill → expense<br/>GET /{id}/bill → JPEG · DELETE /{id} → message<br/><br/>Config · /api/config<br/>GET / → public config · GET /all → configs<br/>PUT / · key + value → config<br/><br/>Off days · /api/off-days<br/>GET /, /check/{date} → days/status<br/>POST · date range + reason → day<br/>DELETE /{id} → detail"]
            REPORTS["Reports · /api/reports [admin]<br/>GET /vote-vs-attendance · date range → rows<br/>GET /meal-summary · date range → rows<br/>GET /ratings-summary · date range → rows<br/>GET /user-report/{id} · date range → records<br/>GET /export-pdf · filters → PDF<br/><br/>Meta · /api/version → build info<br/>GET /api/health → status"]
        end

        GUARDS["Shared dependencies<br/>Pydantic validation · DB session<br/>JWT/user · admin · mess-duty access"]
        RULES["Route business rules<br/>Time windows · ownership · aggregation"]
        FastAPI --> ENDPOINTS
        ENDPOINTS --> GUARDS
        ENDPOINTS --> RULES
    end

    subgraph DATA["4 · Persistence & services"]
        direction LR
        ORM["SQLAlchemy ORM / SessionLocal"]
        TABLES["Tables<br/>users · meal_types · menu_items · votes<br/>attendance · ratings · duty · expenses<br/>summaries · config · off-days"]
        DB["DATABASE_URL<br/>SQLite default"]
        FILES["Expense bills<br/>Pillow → JPEG<br/>uploads/expenses"]
        PDF["ReportLab<br/>PDF generation"]
        ORM --> TABLES --> DB
        FILES --> UPLOADS["GET /uploads/{path}<br/>Static files"]
    end

    subgraph RETURN["5 · Response"]
        direction LR
        RESPONSE["HTTP response<br/>JSON · error detail · JPEG · XLSX · PDF"]
        VIEW["Axios → Vue view<br/>Update UI or show error"]
    end

    RULES --> ORM
    RULES --> FILES
    RULES --> PDF
    DB --> RESPONSE
    FILES --> RESPONSE
    PDF --> RESPONSE
    UPLOADS --> HTTP
    FastAPI --> RESPONSE
    RESPONSE -. "response via HTTPS" .-> HTTP
    HTTP --> VIEW
    VIEW --> SPA
    HTTP -. "request" .-> FastAPI
```

### Conventions

- Protected routes require a valid JWT. Admin and mess-duty access are enforced by backend dependencies.
- JSON bodies are validated by Pydantic; response shapes are shown after `→`. Uploads and downloads use multipart or binary responses.
- API errors use HTTP status codes and, where provided, a JSON `detail`. The frontend redirects to login on `401`.
- Database and upload locations are deployment-configured; `DATABASE_URL` defaults to SQLite.
