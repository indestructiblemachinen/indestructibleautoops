# ECO 命名空間規範 (ECO Namespace Specification)

**版本**: 1.0.0
**日期**: 2026-02-25
**適用範圍**: `eco-base` 企業級平台全生態系統
**治理等級**: 憲章級 (Constitutional) — 違反即觸發零容忍執行

---

## 1. 前言 (Introduction)

本文件定義 `eco-base` 企業級平台中所有組件的命名空間規範，確保系統在設計、開發、部署與維護生命週期中的一致性、可追溯性與可治理性。

本規範嚴格遵循零信任架構原則，並考量多雲、多環境與多租戶的複雜性，以實現全機器自動化治理。所有平台組件、服務、資源與配置均須符合本規範。

### 1.1. 規範約束力 (Normative Authority)

- 所有新組件與資源須通過 OPA 政策驗證，確保符合本規範
- 違反命名規範的資源將被 CI/CD 管線拒絕合併
- Pre-commit hooks 於本地開發階段即時攔截不合規命名

---

## 2. 命名空間前綴與命名規則 (Naming & Prefix Rules)

### 2.1. 通用命名約定 (General Naming Conventions)

所有命名均採用以下約定：

- **小寫字母**、**數字**與**連字符 `-`** 為唯一允許字元
- **禁止**使用底線 `_`、大寫字母或其他特殊字元
- 前綴用於明確區分實體類型，提供快速識別能力
- 單詞間以連字符 `-` 連接，如 `api-gateway`（非 `apigateway` 或 `api_gateway`）

### 2.2. 核心前綴 (Core Prefixes)

| 前綴 (Prefix) | 用途 (Purpose) | 範例 (Example) |
|---|---|---|
| `eco-` | 平台級通用資源，表示屬於 `eco-base` 生態系統 | `eco-base`, `eco-system`, `eco-deploy-sa` |
| `gl-` | 治理層 (Governance Layer) 資源，對應 GL00-99 語義層級 | `gl-ecosystem-v1`, `gl-ai-superai`, `gl-gov-ops` |
| `ng-` | 新世代治理框架 (NG Framework) 資源，對應 NG100-999 | `ng-governance`, `ng-era1`, `ng-era2` |
| `core-` | 共享內核（控制平面）服務 | `core-auth`, `core-memory-hub`, `core-registry` |
| `svc-` | 微服務實例 | `svc-ai-engine`, `svc-api-gateway`, `svc-etl` |
| `gov-` | 治理引擎相關服務與基礎設施 | `gov-engine`, `gov-validator`, `gov-reporter` |

### 2.3. 平台前綴 (Platform Prefixes)

平台使用語義化域名而非數字 ID。以下為已註冊平台：

| 平台前綴 (Platform Prefix) | 全稱 (Full Name) | K8s 命名空間 (Namespace) | API 端口 (Port) |
|---|---|---|---|
| `superai-` | Super AI Operations Platform | `superai` | 8000 |
| `govops-` | Governance Operations Platform | `govops` | 8090 |
| `seccompops-` | Security & Compliance Operations Platform | `seccompops` | 8095 |
| `dataops-` | Data Operations Platform | `dataops` | 8093 |
| `observops-` | Observability Operations Platform | `observops` | -- |

### 2.4. 資源命名模式 (Resource Naming Pattern)

所有資源命名遵循以下模式：

```
<domain>-<component>[-<purpose>][-<qualifier>]
```

- **`<domain>`**: 資源所屬域，即核心前綴或平台前綴
- **`<component>`**: 資源所屬的組件或服務名稱
- **`<purpose>`**: 資源的用途或功能（可選）
- **`<qualifier>`**: 環境、區域或版本限定符（可選）

**範例：**

| 資源類型 | 命名 | 說明 |
|---|---|---|
| K8s Namespace | `superai` | 平台頂層命名空間 |
| K8s Deployment | `superai-ai-engine-prod` | SuperAI 平台 AI 引擎生產部署 |
| Docker Container | `gov-engine` | 治理引擎容器 |
| Docker Container | `gov-validator` | 治理驗證器容器 |
| Docker Container | `gov-postgres` | 治理引擎 PostgreSQL 實例 |
| Helm Release | `govops-platform-prod` | GovOps 平台生產 Helm 釋出 |
| Service Account | `eco-deploy-sa` | 平台級部署服務帳號 |
| OPA Policy | `gov-policy-zero-tolerance` | 零容忍治理策略 |
| GitHub Workflow | `ci-govops-test` | GovOps 平台 CI 測試工作流 |
| GitHub Secret | `SUPERAI_DB_PASSWORD` | SuperAI 平台資料庫密碼 |

---

## 3. 標籤與註解 (Labels & Annotations)

所有可部署資源（K8s 資源、Docker 容器、Cloudflare Workers）必須包含標準化標籤與註解。

### 3.1. 強制標籤 (Mandatory Labels)

| 標籤鍵 (Label Key) | 描述 (Description) | 範例 (Example) |
|---|---|---|
| `app.kubernetes.io/name` | 應用程式名稱 | `ai-engine` |
| `app.kubernetes.io/instance` | 應用程式實例名稱 | `ai-engine-prod` |
| `app.kubernetes.io/version` | 應用程式版本 | `1.2.3` |
| `app.kubernetes.io/component` | 組件角色 | `backend`, `worker`, `gateway` |
| `app.kubernetes.io/part-of` | 所屬平台 | `superai-platform` |
| `app.kubernetes.io/managed-by` | 管理工具 | `kustomize`, `helm`, `kubectl` |
| `eco-base.io/platform` | 所屬業務域平台 | `superai`, `govops`, `seccompops` |
| `eco-base.io/environment` | 部署環境 | `production`, `staging`, `development` |
| `eco-base.io/owner` | 負責團隊 | `platform-team`, `governance-team` |

### 3.2. 強制註解 (Mandatory Annotations)

| 註解鍵 (Annotation Key) | 描述 (Description) | 範例 (Example) |
|---|---|---|
| `eco-base.io/uri` | 資源 URI | `eco-base://k8s/superai/deployment/ai-engine` |
| `eco-base.io/urn` | 資源 URN | `urn:eco-base:k8s:superai:deployment:ai-engine:<uuid>` |
| `eco-base.io/governance-policy` | 適用的治理策略 | `zero-tolerance.rego` |
| `eco-base.io/audit-log-level` | 審計日誌級別 | `full`, `minimal` |

### 3.3. 標籤命名規則 (Label Naming Rules)

- Kubernetes 標準標籤使用 `app.kubernetes.io/` 前綴
- 平台自訂標籤統一使用 `eco-base.io/` 前綴
- 治理相關標籤使用 `governance.io/` 前綴
- 標籤值遵循與資源命名相同的字元約定（小寫、連字符）

---

## 4. 資源映射與引用規範 (Resource Mapping & Reference Specification)

### 4.1. URI 規範 (URI Specification)

URI 用於識別資源的位置與訪問路徑：

```
eco-base://<resource-type>/<platform>/<component>/<resource-name>[?<query-params>]
```

| 欄位 | 描述 | 允許值 |
|---|---|---|
| `eco-base://` | 平台協議前綴 | 固定值 |
| `<resource-type>` | 資源類型 | `k8s`, `service`, `policy`, `document`, `artifact` |
| `<platform>` | 所屬平台 | `superai`, `govops`, `seccompops`, `dataops`, `observops`, `core` |
| `<component>` | 組件名稱 | `deployment`, `service`, `configmap`, `policy`, `workflow` |
| `<resource-name>` | 資源具體名稱 | 遵循通用命名約定 |
| `[?<query-params>]` | 查詢參數（可選） | `?version=1.2.3`, `?env=production` |

**範例：**

```
eco-base://k8s/superai/deployment/ai-engine
eco-base://k8s/govops/deployment/gov-engine
eco-base://policy/core/governance/zero-tolerance
eco-base://service/seccompops/api/compliance-checker
eco-base://document/core/architecture/namespace-spec
```

### 4.2. URN 規範 (URN Specification)

URN 用於資源的持久性唯一識別，不依賴位置：

```
urn:eco-base:<resource-type>:<platform>:<component>:<resource-name>:<unique-id>
```

| 欄位 | 描述 | 格式 |
|---|---|---|
| `urn:eco-base:` | 平台 URN 前綴 | 固定值 |
| `<resource-type>` | 資源類型 | 同 URI 規範 |
| `<platform>` | 所屬平台 | 同 URI 規範 |
| `<component>` | 組件名稱 | 同 URI 規範 |
| `<resource-name>` | 資源具體名稱 | 同 URI 規範 |
| `<unique-id>` | 全局唯一識別符 | UUIDv4 或 SHA-256 前 12 位 |

**範例：**

```
urn:eco-base:k8s:superai:deployment:ai-engine:6ba7b811-9dad-11d1-80b4-00c04fd430c8
urn:eco-base:policy:core:governance:zero-tolerance:sha256-a1b2c3d4e5f6
urn:eco-base:service:govops:api:etl-pipeline:f47ac10b-58cc-4372-a567-0e02b2c3d479
```

### 4.3. 內部引用機制 (Internal Reference Mechanism)

平台內部組件之間引用其他資源時：

- **持久引用**：使用 URN 進行跨生命週期識別
- **訪問引用**：通過服務發現或配置管理系統將 URN 解析為 URI 或具體地址
- **配置引用**：在 YAML 配置文件中，引用外部服務或策略時使用 URN
- **日誌與審計**：所有日誌與審計事件必須包含相關資源的 URN
- **API 契約**：API 契約中的資源類型與 ID 須與 URN 結構一致

---

## 5. 環境變數命名規範 (Environment Variable Naming Specification)

### 5.1. 命名模式 (Naming Pattern)

環境變數使用**大寫字母**與**底線 `_`**，以平台或組件前綴開頭：

```
ECO_<COMPONENT>_<SETTING>              # 平台級通用變數
<PLATFORM>_<COMPONENT>_<SETTING>       # 特定平台變數
GL_<SUBSYSTEM>_<SETTING>               # 治理引擎變數
```

### 5.2. 前綴對照表 (Prefix Mapping)

| 前綴 | 適用範圍 | 實施狀態 | 範例 |
|---|---|---|---|
| `ECO_` | 平台級通用配置 | 規劃中 | `ECO_LOG_LEVEL`, `ECO_DEPLOY_MODE` |
| `SUPERAI_` | SuperAI 平台 | **待遷移** (現用 `APP_*`, `DATABASE_*`) | `SUPERAI_API_PORT`, `SUPERAI_DB_HOST` |
| `GOVOPS_` | GovOps 平台 | 已實施 | `GOVOPS_ENV`, `GOVOPS_DB_HOST` |
| `SECCOMPOPS_` | SecCompOps 平台 | 已實施 | `SECCOMPOPS_ENV`, `SECCOMPOPS_DB_HOST` |
| `DATAOPS_` | DataOps 平台 | 已實施 | `DATAOPS_ENV`, `DATAOPS_DB_HOST` |
| `OBSERVOPS_` | ObservOps 平台 | 規劃中 | `OBSERVOPS_API_PORT`, `OBSERVOPS_DB_HOST` |
| `GL_` | 治理引擎 | 已實施 | `GL_ENGINE_LOG_LEVEL`, `GL_ENGINE_LOG_DIR` |

### 5.3. 通用環境變數 (Common Variables)

以下為各平台共通的環境變數模板（以 `<PLATFORM>` 代指平台前綴）：

| 變數名稱 | 描述 | 範例值 |
|---|---|---|
| `<PLATFORM>_API_PORT` | API 服務端口 | `8090` |
| `<PLATFORM>_METRICS_PORT` | Metrics 端口 | `9090` |
| `<PLATFORM>_DB_HOST` | 資料庫主機 | `db.superai.svc.cluster.local` |
| `<PLATFORM>_DB_PORT` | 資料庫端口 | `5432` |
| `<PLATFORM>_DB_NAME` | 資料庫名稱 | `superai_db` |
| `<PLATFORM>_REDIS_URL` | Redis 連線 URL | `redis://redis.superai.svc.cluster.local:6379` |
| `<PLATFORM>_LOG_LEVEL` | 日誌等級 | `INFO`, `DEBUG`, `WARNING` |

### 5.4. 第三方服務變數 (Third-Party Service Variables)

第三方服務可使用其官方推薦的命名，但須在內部配置文件中建立明確映射：

| 第三方變數 | 內部映射 | 來源 |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | `ECO_CF_API_TOKEN` | Cloudflare |
| `GITHUB_TOKEN` | `ECO_GH_TOKEN` | GitHub Actions |
| `SUPABASE_URL` | `ECO_SUPABASE_URL` | Supabase |

### 5.5. 敏感資訊處理 (Sensitive Information Handling)

所有敏感資訊必須通過 Secrets 管理系統進行管理：

| 管理系統 | 適用場景 | 變數來源 |
|---|---|---|
| GitHub Secrets | CI/CD 管線 | `GH_TOKEN`, `SUPABASE_ANON_KEY` |
| Kubernetes Secrets | K8s 部署 | `<PLATFORM>_DB_PASSWORD` |
| HashiCorp Vault | 跨環境 Secrets 管理 | 動態注入 |

**鐵律**：敏感資訊**絕不**硬編碼於程式碼或配置文件。環境變數僅引用 Secrets 名稱或路徑，不包含實際值。

---

## 6. 依賴關係管理 (Dependency Management)

### 6.1. 服務間通信 (Inter-Service Communication)

- 服務通過 K8s Service Name 進行通信，禁止直接使用 IP
- DNS 格式：`<service>.<namespace>.svc.cluster.local`
- 範例：`gov-engine.govops.svc.cluster.local:8091`

### 6.2. 版本控制 (Version Control)

外部依賴版本須於下列文件中明確鎖定：

| 語言 | 版本文件 | 範例 |
|---|---|---|
| Python | `pyproject.toml` | `fastapi>=0.115,<1` |
| Node.js | `package.json` | `"next": "^14.0.0"` |
| Go | `go.mod` | `require github.com/... v1.2.3` |
| Kubernetes | `kustomization.yaml` | `images.newTag: 1.2.3` |

### 6.3. API 契約 (API Contracts)

- 服務間通信基於 OpenAPI 3.1 或 AsyncAPI 2.6 契約
- 契約文件存放於各平台的 `docs/api/` 目錄
- 版本變更須通過向後相容性檢查

---

## 7. 平台端口分配 (Platform Port Allocation)

所有平台的端口分配須全局唯一，避免衝突。

### 7.1. 核心引擎 (Core Engine)

| 服務 | Host Port | 說明 |
|---|---|---|
| `gov-engine` | 8080 | 根層治理引擎 (root docker-compose) |
| `gov-postgres` | 5432 | 根層 PostgreSQL |
| `gov-redis` | 6379 | 根層 Redis |
| `gov-prometheus` | 9090 | 根層 Prometheus |

### 7.2. 平台端口矩陣 (Platform Port Matrix)

以下為各平台 `docker-compose.yaml` 中的**實際**端口映射：

| 平台 | API Port | Metrics Port | PostgreSQL Port | Redis Port |
|---|---|---|---|---|
| `superai` | 8000 | 9090 (via `$PROMETHEUS_PORT`) | 5432 (via `$POSTGRES_PORT`) | 6379 (via `$REDIS_PORT`) |
| `govops` | 8090 | 9090 | 5432 | 6379 |
| `dataops` | 8093 | 9094 | 5435 | 6382 |
| `seccompops` | 8095 | 9092 | 5434 | 6381 |
| `observops` | -- | -- | -- | -- |

> **注意**：`superai` 與 `govops` 的 PostgreSQL/Redis/Metrics 端口在獨立運行時使用相同默認值。
> 多平台共存時須通過環境變數覆蓋以避免衝突。`superai` 支持 `$APP_PORT`、`$POSTGRES_PORT`、`$REDIS_PORT`、`$PROMETHEUS_PORT` 環境變數覆蓋。

### 7.3. 端口範圍保留 (Reserved Port Ranges)

- **8000-8099**: 平台 API 服務
- **9090-9099**: 平台 Metrics 服務（Prometheus）
- **5432-5439**: 平台 PostgreSQL 實例
- **6379-6389**: 平台 Redis 實例

---

## 8. 目錄結構命名規範 (Directory Structure Naming)

### 8.1. 平台目錄結構 (Platform Directory Layout)

所有平台遵循統一的目錄佈局：

```
<platform-name>/
├── src/                    # 源碼目錄
│   ├── domain/             # 領域層
│   ├── engine/             # 引擎層
│   ├── infrastructure/     # 基礎設施層
│   └── presentation/       # 展示層（API）
├── tests/                  # 測試目錄
├── k8s/                    # Kubernetes 配置
│   ├── base/               # 基礎配置（含 namespace.yaml）
│   └── overlays/           # 環境覆蓋層
│       ├── development/
│       ├── staging/
│       └── production/
├── helm/                   # Helm Chart
├── monitoring/             # 監控配置
├── scripts/                # 工具腳本
├── docs/                   # 文檔
├── pyproject.toml          # Python 專案配置
├── Dockerfile.prod         # 生產 Docker 鏡像
└── docker-compose.yaml     # 本地開發編排
```

### 8.2. 目錄命名約定 (Directory Naming Conventions)

- 頂層平台目錄：`<name>-platform`（如 `superai-platform`, `govops-platform`）
- K8s 命名空間名稱與平台短名一致（如 `superai`, `govops`）
- 配置文件使用 `.yaml` 副檔名（非 `.yml`）
- 測試文件以 `test_` 前綴命名

---

## 9. GitHub 資源命名規範 (GitHub Resource Naming)

### 9.1. GitHub Actions Workflow

工作流文件命名模式：`<trigger>-<platform>-<action>.yaml`

| 範例 | 說明 |
|---|---|
| `ci-superai-test.yaml` | SuperAI 平台 CI 測試 |
| `ci-govops-lint.yaml` | GovOps 平台 CI Lint |
| `cd-seccompops-deploy.yaml` | SecCompOps 平台 CD 部署 |
| `schedule-eco-audit.yaml` | 平台級定期審計 |

### 9.2. GitHub Secrets

Secret 命名遵循環境變數規範（大寫底線），並以平台前綴區分：

| 範例 | 說明 |
|---|---|
| `SUPERAI_DB_PASSWORD` | SuperAI 資料庫密碼 |
| `GOVOPS_API_KEY` | GovOps API 金鑰 |
| `ECO_DEPLOY_TOKEN` | 平台級部署令牌 |
| `GCP_SA_EMAIL` | 第三方雲服務帳號 |

### 9.3. Git Branch 命名

分支命名模式：`<type>/<platform-or-scope>/<description>`

| 範例 | 說明 |
|---|---|
| `feature/superai/add-vector-search` | SuperAI 新功能 |
| `fix/govops/etl-pipeline-timeout` | GovOps 錯誤修復 |
| `chore/eco/update-dependencies` | 平台級依賴更新 |

---

## 10. 命名驗證與執行 (Naming Validation & Enforcement)

### 10.1. 自動化驗證層級 (Validation Layers)

| 層級 | 工具 | 觸發時機 |
|---|---|---|
| 本地開發 | Pre-commit hooks | `git commit` 前 |
| CI 管線 | OPA / Rego 政策 | PR 建立時 |
| K8s 部署 | Gatekeeper / Kyverno | `kubectl apply` 時 |
| 運行時 | Admission Webhook | 資源建立 / 修改時 |

### 10.2. 零容忍規則 (Zero-Tolerance Rules)

以下違規將被自動攔截，不允許例外：

- 命名空間或資源名稱含有大寫字母或底線
- 缺少強制標籤 (`app.kubernetes.io/name`, `eco-base.io/platform`)
- K8s 資源未包含 URI / URN 註解
- 環境變數名稱不符合前綴規範
- 端口分配與已註冊端口衝突

---

## 11. 總結 (Summary)

本規範為 `eco-base` 平台提供統一、嚴謹的命名與引用標準。核心原則：

1. **語義化命名**：所有資源名稱具備自描述性，一看即知其所屬域與用途
2. **前綴分層**：通過 `eco-` / `gl-` / `ng-` / `gov-` / 平台前綴實現快速分類
3. **全局唯一**：URI + URN 雙重識別確保資源在整個生態系統中可尋址、可追溯
4. **機器可治理**：所有規則均可通過 OPA 政策自動驗證與執行
5. **零容忍執行**：不合規命名在開發、CI、部署三道關卡均被攔截
