#!/usr/bin/env python3
#
# @GL-governed
# @GL-layer: GL30-49
# @GL-semantic: governance-enforcement
# @GL-audit-trail: ./governance/GL_SEMANTIC_ANCHOR.json
#
"""
統一的生態系統強制執行入口點
Unified Ecosystem Enforcement Entry Point

版本: 2.0.0
用途: 提供單一命令來執行所有生態系統治理檢查
作者: Machine Native Ops Team
日期: 2026-02-03

MNGA (Machine Native Governance Architecture) 強制執行器
- 真正執行治理檢查，不允許假 PASS
- 掃描所有文件的 GL 合規性
- 驗證命名規範
- 檢查證據鏈完整性
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from collections import Counter

# 添加 ecosystem 到路徑
ECOSYSTEM_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = ECOSYSTEM_ROOT.parent

# 根目錄 ecosystem 僅包含入口時，回退到完整實作目錄
CANONICAL_ECOSYSTEM_ROOT = (
    WORKSPACE_ROOT
    / "governance"
    / "l3_execution"
    / "boundaries"
    / "namespace-governance-boundary"
    / "implementation"
    / "ecosystem"
)

if not (ECOSYSTEM_ROOT / "governance").exists() and CANONICAL_ECOSYSTEM_ROOT.exists():
    ECOSYSTEM_ROOT = CANONICAL_ECOSYSTEM_ROOT
    WORKSPACE_ROOT = ECOSYSTEM_ROOT.parent

sys.path.insert(0, str(ECOSYSTEM_ROOT))


# 顏色輸出
class Colors:
    """ANSI 顏色代碼"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    """打印標題"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}\n")


def print_step(number: int, text: str):
    """打印步驟"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{number}️⃣  {text}{Colors.END}")


def print_success(text: str):
    """打印成功訊息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """打印錯誤訊息"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """打印警告訊息"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    """打印資訊"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


@dataclass
class Violation:
    """治理違規"""

    rule_id: str
    file_path: str
    line_number: Optional[int]
    message: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    suggestion: str


@dataclass
class EnforcementResult:
    """強制執行結果"""

    check_name: str
    passed: bool
    message: str
    violations: List[Violation] = field(default_factory=list)
    files_scanned: int = 0
    execution_time_ms: int = 0


# ============================================================================
# MNGA 核心檢查器
# ============================================================================


class MNGAEnforcer:
    """Machine Native Governance Architecture 強制執行器"""

    def __init__(self, workspace_path: Path = WORKSPACE_ROOT):
        self.workspace = workspace_path
        self.ecosystem = workspace_path / "ecosystem"
        self.violations: List[Violation] = []
        self.files_scanned = 0

        # GL 命名規範
        self.naming_patterns = {
            "kebab-case": re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$"),
            "snake_case": re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$"),
            "PascalCase": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),
            "camelCase": re.compile(r"^[a-z][a-zA-Z0-9]*$"),
        }

        # 禁止的模式 - 更精確的正則表達式
        self.forbidden_patterns = [
            (r"github_pat_[A-Za-z0-9_]{30,}", "GitHub Personal Access Token exposed"),
            (r"ghp_[A-Za-z0-9]{36,}", "GitHub Token exposed"),
            (r"sk-[A-Za-z0-9]{32,}", "OpenAI API Key exposed"),
            (r"sk-proj-[A-Za-z0-9_-]{40,}", "OpenAI Project API Key exposed"),
            (r"xoxb-[A-Za-z0-9-]+", "Slack Bot Token exposed"),
            (r"xoxp-[A-Za-z0-9-]+", "Slack User Token exposed"),
            (r"AKIA[A-Z0-9]{16}", "AWS Access Key exposed"),
        ]

        # 排除的佔位符模式
        self.placeholder_patterns = [
            r"\$\{[A-Z_]+\}",  # ${ENV_VAR}
            r"change-me",
            r"your-.*-here",
            r"example",
            r"placeholder",
            r"xxx+",
            r"\*+",
            r"<[A-Z_]+>",  # <YOUR_TOKEN>
        ]

        # GL 層級定義
        self.gl_layers = {
            "GL00-09": "Infrastructure Foundation",
            "GL10-19": "Core Services",
            "GL20-29": "Language Behavior - Naming",
            "GL30-39": "Language Behavior - Execution",
            "GL40-49": "Language Behavior - Validation",
            "GL50-59": "Format Layer - Structure",
            "GL60-69": "Format Layer - Schema",
            "GL70-79": "Format Layer - Evidence",
            "GL80-89": "Format Layer - Audit",
            "GL90-99": "Meta-Specification",
        }

    def run_all_checks(self) -> List[EnforcementResult]:
        """執行所有 MNGA 檢查"""
        results = []

        # 1. GL 合規性檢查
        results.append(self.check_gl_compliance())

        # 2. 命名規範檢查
        results.append(self.check_naming_conventions())

        # 3. 安全性檢查
        results.append(self.check_security())

        # 4. 證據鏈完整性檢查
        results.append(self.check_evidence_chain())

        # 5. 治理執行器檢查
        results.append(self.check_governance_enforcer())

        # 6. 自我審計檢查
        results.append(self.check_self_auditor())

        # 7. MNGA 架構完整性檢查
        results.append(self.check_mnga_architecture())
        results.append(self.check_foundation_layer())
        results.append(self.check_coordination_layer())
        results.append(self.check_governance_engines())
        results.append(self.check_tools_layer())
        results.append(self.check_events_layer())
        results.append(self.check_complete_naming_enforcer())
        results.append(self.check_enforcers_completeness())
        results.append(self.check_coordination_services())
        results.append(self.check_meta_governance_systems())
        results.append(self.check_reasoning_system())
        results.append(self.check_validators_layer())

        return results

    def check_gl_compliance(self) -> EnforcementResult:
        """檢查 GL 治理合規性"""
        start_time = datetime.now()
        violations = []
        files_scanned = 0

        # 必須存在的治理文件
        required_files = [
            self.ecosystem / "governance" / "governance-manifest.yaml",
            self.ecosystem / "governance" / "GL-SEMANTIC-ANCHOR.json",
            self.ecosystem / "contracts",
            self.ecosystem / "enforcers",
        ]

        for req_file in required_files:
            if not req_file.exists():
                violations.append(
                    Violation(
                        rule_id="GL-COMPLIANCE-001",
                        file_path=str(req_file),
                        line_number=None,
                        message=f"必要的治理文件缺失: {req_file.name}",
                        severity="CRITICAL",
                        suggestion=f"創建 {req_file} 文件",
                    )
                )

        # 掃描 Python 文件的 GL 標註
        python_files = list(self.ecosystem.rglob("*.py"))
        for py_file in python_files:
            files_scanned += 1
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                # 檢查是否有 GL 標註
                if not re.search(r"@GL-governed|@GL-layer|GL\d{2}", content):
                    # 只對核心文件要求 GL 標註
                    if "enforcer" in py_file.name or "audit" in py_file.name:
                        violations.append(
                            Violation(
                                rule_id="GL-COMPLIANCE-002",
                                file_path=str(py_file.relative_to(self.workspace)),
                                line_number=1,
                                message="核心治理文件缺少 GL 標註",
                                severity="MEDIUM",
                                suggestion="添加 @GL-governed 和 @GL-layer 標註",
                            )
                        )
            except Exception as e:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        return EnforcementResult(
            check_name="GL Compliance",
            passed=len([v for v in violations if v.severity == "CRITICAL"]) == 0,
            message=f"掃描 {files_scanned} 個文件，發現 {len(violations)} 個問題",
            violations=violations,
            files_scanned=files_scanned,
            execution_time_ms=int(elapsed),
        )

    def check_naming_conventions(self) -> EnforcementResult:
        """檢查命名規範 (GL20-29) - 使用完整命名檢查器"""
        start_time = datetime.now()
        violations = []
        files_scanned = 0
        dirs_scanned = 0

        # 特殊目錄例外
        special_dir_exceptions = {
            ".github",
            "PULL_REQUEST_TEMPLATE",
            "ISSUE_TEMPLATE",
            "(tabs)",
            "(auth)",
            "(app)",
            "RUNBOOKS",
            "TRAINING",
            "MIGRATION",
        }

        # GL 語義目錄模式
        gl_semantic_pattern = re.compile(r"^GL\d{2}(-\d{2})?(-[A-Za-z-]+)?$")

        # 排除目錄
        excluded_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            ".idea",
            ".vscode",
            "outputs",
            ".governance",
        }

        def should_exclude(path: Path) -> bool:
            for part in path.parts:
                if part in excluded_dirs:
                    return True
            return False

        # 1. 檢查目錄命名
        for dir_path in self.workspace.rglob("*"):
            if not dir_path.is_dir():
                continue
            if should_exclude(dir_path):
                continue

            dirs_scanned += 1
            dir_name = dir_path.name

            # 跳過特殊目錄
            if dir_name in special_dir_exceptions:
                continue
            if gl_semantic_pattern.match(dir_name):
                continue
            if dir_name.startswith(".") or dir_name.startswith("__"):
                continue

            # Python 包目錄允許 snake_case
            if (dir_path / "__init__.py").exists():
                continue

            # 檢查下劃線（應使用連字符）
            if "_" in dir_name:
                violations.append(
                    Violation(
                        rule_id="GL20-NAMING-001",
                        file_path=str(dir_path.relative_to(self.workspace)),
                        line_number=None,
                        message=f"目錄 '{dir_name}' 使用下劃線，應使用連字符 (kebab-case)",
                        severity="MEDIUM",
                        suggestion=f"重命名為 '{dir_name.replace('_', '-')}'",
                    )
                )

        # 2. 檢查 Python 文件命名（應使用 snake_case）
        for file_path in self.workspace.rglob("*.py"):
            if should_exclude(file_path):
                continue

            files_scanned += 1
            name = file_path.name
            stem = file_path.stem

            # 跳過特殊文件
            if name.startswith("__") and name.endswith("__.py"):
                continue

            # Python 文件應使用 snake_case，不應有連字符
            if "-" in stem:
                violations.append(
                    Violation(
                        rule_id="GL20-NAMING-002",
                        file_path=str(file_path.relative_to(self.workspace)),
                        line_number=None,
                        message=f"Python 文件 '{name}' 使用連字符，應使用下劃線 (snake_case)",
                        severity="HIGH",
                        suggestion=f"重命名為 '{stem.replace('-', '_')}.py'",
                    )
                )

        # 3. 檢查配置文件命名（應使用 kebab-case）
        for ext in [".yaml", ".yml", ".json"]:
            for file_path in self.workspace.rglob(f"*{ext}"):
                if should_exclude(file_path):
                    continue

                files_scanned += 1
                name = file_path.name
                stem = file_path.stem

                # 跳過特殊文件
                if name in {"package.json", "package-lock.json", "tsconfig.json"}:
                    continue
                # 跳過 GL 語義文件
                if stem.startswith("GL") and re.match(r"^GL\d{2}", stem):
                    continue

                # 配置文件應使用 kebab-case，不應有下劃線
                if "_" in stem:
                    violations.append(
                        Violation(
                            rule_id="GL20-NAMING-003",
                            file_path=str(file_path.relative_to(self.workspace)),
                            line_number=None,
                            message=f"配置文件 '{name}' 使用下劃線，應使用連字符 (kebab-case)",
                            severity="MEDIUM",
                            suggestion=f"重命名為 '{stem.replace('_', '-')}{ext}'",
                        )
                    )

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        # 只有 HIGH 和 CRITICAL 才算失敗
        critical_violations = [
            v for v in violations if v.severity in ["CRITICAL", "HIGH"]
        ]

        return EnforcementResult(
            check_name="Naming Conventions",
            passed=len(critical_violations) == 0,
            message=f"掃描 {dirs_scanned} 個目錄和 {files_scanned} 個文件，發現 {len(violations)} 個命名問題",
            violations=violations,
            files_scanned=dirs_scanned + files_scanned,
            execution_time_ms=int(elapsed),
        )

    def check_security(self) -> EnforcementResult:
        """安全性檢查 - 檢測敏感信息洩露"""
        start_time = datetime.now()
        violations = []
        files_scanned = 0

        # 掃描所有文本文件
        text_extensions = [
            ".py",
            ".js",
            ".ts",
            ".yaml",
            ".yml",
            ".json",
            ".md",
            ".txt",
            ".sh",
        ]

        for ext in text_extensions:
            for file_path in self.workspace.rglob(f"*{ext}"):
                # 排除特定目錄（包括敏感數據目錄）
                if any(
                    p in str(file_path)
                    for p in [
                        ".git",
                        "node_modules",
                        "__pycache__",
                        "outputs",
                        "summarized_conversations",
                        "summarized-conversations",
                    ]
                ):
                    continue

                files_scanned += 1
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")

                    for pattern, description in self.forbidden_patterns:
                        matches = list(re.finditer(pattern, content))
                        for match in matches:
                            matched_text = match.group()

                            # 檢查是否為佔位符
                            is_placeholder = False
                            for placeholder in self.placeholder_patterns:
                                if re.search(placeholder, matched_text, re.IGNORECASE):
                                    is_placeholder = True
                                    break

                            # 獲取匹配行的上下文
                            line_start = content.rfind("\n", 0, match.start()) + 1
                            line_end = content.find("\n", match.end())
                            if line_end == -1:
                                line_end = len(content)
                            line_content = content[line_start:line_end]

                            # 檢查行內容是否包含佔位符
                            for placeholder in self.placeholder_patterns:
                                if re.search(placeholder, line_content, re.IGNORECASE):
                                    is_placeholder = True
                                    break

                            if not is_placeholder:
                                # 計算行號
                                line_num = content[: match.start()].count("\n") + 1
                                violations.append(
                                    Violation(
                                        rule_id="GL-SECURITY-001",
                                        file_path=str(
                                            file_path.relative_to(self.workspace)
                                        ),
                                        line_number=line_num,
                                        message=description,
                                        severity="CRITICAL",
                                        suggestion="移除敏感信息並添加到 .gitignore",
                                    )
                                )
                except Exception:
                    pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        return EnforcementResult(
            check_name="Security Check",
            passed=len(violations) == 0,
            message=f"掃描 {files_scanned} 個文件，發現 {len(violations)} 個安全問題",
            violations=violations,
            files_scanned=files_scanned,
            execution_time_ms=int(elapsed),
        )

    def check_evidence_chain(self) -> EnforcementResult:
        """檢查證據鏈完整性 (GL70-79)"""
        start_time = datetime.now()
        violations = []
        files_scanned = 0

        # 檢查 .governance 目錄
        governance_dirs = list(self.workspace.rglob(".governance"))

        for gov_dir in governance_dirs:
            files_scanned += 1

            # 檢查必要的證據文件
            event_stream = gov_dir / "event-stream.jsonl"
            if not event_stream.exists():
                violations.append(
                    Violation(
                        rule_id="GL70-EVIDENCE-001",
                        file_path=str(gov_dir.relative_to(self.workspace)),
                        line_number=None,
                        message="缺少 event-stream.jsonl 證據文件",
                        severity="MEDIUM",
                        suggestion="創建 event-stream.jsonl 來記錄治理事件",
                    )
                )

        # 檢查審計日誌目錄
        audit_logs_dir = self.ecosystem / "logs" / "audit-logs"
        if audit_logs_dir.exists():
            log_files = list(audit_logs_dir.rglob("*.json"))
            files_scanned += len(log_files)

            if len(log_files) == 0:
                violations.append(
                    Violation(
                        rule_id="GL70-EVIDENCE-002",
                        file_path=str(audit_logs_dir.relative_to(self.workspace)),
                        line_number=None,
                        message="審計日誌目錄為空",
                        severity="LOW",
                        suggestion="確保審計日誌正在被記錄",
                    )
                )

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        return EnforcementResult(
            check_name="Evidence Chain",
            passed=len([v for v in violations if v.severity == "CRITICAL"]) == 0,
            message=f"檢查 {files_scanned} 個證據源，發現 {len(violations)} 個問題",
            violations=violations,
            files_scanned=files_scanned,
            execution_time_ms=int(elapsed),
        )

    def check_governance_enforcer(self) -> EnforcementResult:
        """檢查治理執行器是否正常工作"""
        start_time = datetime.now()
        violations = []

        enforcer_path = self.ecosystem / "enforcers" / "governance_enforcer.py"

        if not enforcer_path.exists():
            return EnforcementResult(
                check_name="Governance Enforcer",
                passed=False,
                message="治理執行器文件不存在",
                violations=[
                    Violation(
                        rule_id="MNGA-ENFORCER-001",
                        file_path="ecosystem/enforcers/governance_enforcer.py",
                        line_number=None,
                        message="治理執行器文件缺失",
                        severity="CRITICAL",
                        suggestion="創建 governance_enforcer.py",
                    )
                ],
                files_scanned=0,
                execution_time_ms=0,
            )

        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "governance_enforcer", enforcer_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if not hasattr(module, "GovernanceEnforcer"):
                    violations.append(
                        Violation(
                            rule_id="MNGA-ENFORCER-002",
                            file_path="ecosystem/enforcers/governance_enforcer.py",
                            line_number=None,
                            message="GovernanceEnforcer 類不存在",
                            severity="CRITICAL",
                            suggestion="定義 GovernanceEnforcer 類",
                        )
                    )
                else:
                    enforcer = module.GovernanceEnforcer()

                    # 檢查必要的方法
                    required_methods = [
                        "before_operation",
                        "after_operation",
                        "check_gates",
                    ]
                    for method in required_methods:
                        if not hasattr(enforcer, method):
                            violations.append(
                                Violation(
                                    rule_id="MNGA-ENFORCER-003",
                                    file_path="ecosystem/enforcers/governance_enforcer.py",
                                    line_number=None,
                                    message=f"缺少必要方法: {method}",
                                    severity="HIGH",
                                    suggestion=f"實現 {method} 方法",
                                )
                            )

                    # 嘗試執行 before_operation
                    if hasattr(enforcer, "before_operation"):
                        try:
                            # 創建測試操作 - 使用正確的參數
                            if hasattr(module, "Operation"):
                                test_op = module.Operation(
                                    name="test_operation",
                                    type="validation",
                                    parameters={"test": True},
                                    timestamp=datetime.now(timezone.utc).isoformat(),
                                )
                                result = enforcer.before_operation(test_op)
                                if result is None:
                                    violations.append(
                                        Violation(
                                            rule_id="MNGA-ENFORCER-004",
                                            file_path="ecosystem/enforcers/governance_enforcer.py",
                                            line_number=None,
                                            message="before_operation 返回 None",
                                            severity="MEDIUM",
                                            suggestion="確保 before_operation 返回有效的執行計劃",
                                        )
                                    )
                        except Exception as e:
                            violations.append(
                                Violation(
                                    rule_id="MNGA-ENFORCER-005",
                                    file_path="ecosystem/enforcers/governance_enforcer.py",
                                    line_number=None,
                                    message=f"before_operation 執行失敗: {str(e)[:100]}",
                                    severity="HIGH",
                                    suggestion="修復 before_operation 方法",
                                )
                            )

        except Exception as e:
            violations.append(
                Violation(
                    rule_id="MNGA-ENFORCER-006",
                    file_path="ecosystem/enforcers/governance_enforcer.py",
                    line_number=None,
                    message=f"無法載入治理執行器: {str(e)[:100]}",
                    severity="CRITICAL",
                    suggestion="修復模組導入錯誤",
                )
            )

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        return EnforcementResult(
            check_name="Governance Enforcer",
            passed=len([v for v in violations if v.severity == "CRITICAL"]) == 0,
            message=f"治理執行器檢查完成，發現 {len(violations)} 個問題",
            violations=violations,
            files_scanned=1,
            execution_time_ms=int(elapsed),
        )

    def check_self_auditor(self) -> EnforcementResult:
        """檢查自我審計器是否正常工作"""
        start_time = datetime.now()
        violations = []

        auditor_path = self.ecosystem / "enforcers" / "self_auditor.py"

        if not auditor_path.exists():
            return EnforcementResult(
                check_name="Self Auditor",
                passed=False,
                message="自我審計器文件不存在",
                violations=[
                    Violation(
                        rule_id="MNGA-AUDITOR-001",
                        file_path="ecosystem/enforcers/self_auditor.py",
                        line_number=None,
                        message="自我審計器文件缺失",
                        severity="CRITICAL",
                        suggestion="創建 self_auditor.py",
                    )
                ],
                files_scanned=0,
                execution_time_ms=0,
            )

        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("self_auditor", auditor_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if not hasattr(module, "SelfAuditor"):
                    violations.append(
                        Violation(
                            rule_id="MNGA-AUDITOR-002",
                            file_path="ecosystem/enforcers/self_auditor.py",
                            line_number=None,
                            message="SelfAuditor 類不存在",
                            severity="CRITICAL",
                            suggestion="定義 SelfAuditor 類",
                        )
                    )
                else:
                    auditor = module.SelfAuditor()

                    # 檢查必要的方法
                    required_methods = [
                        "audit_operation",
                        "generate_audit_report",
                        "scan_audit_logs",
                    ]
                    for method in required_methods:
                        if not hasattr(auditor, method):
                            violations.append(
                                Violation(
                                    rule_id="MNGA-AUDITOR-003",
                                    file_path="ecosystem/enforcers/self_auditor.py",
                                    line_number=None,
                                    message=f"缺少必要方法: {method}",
                                    severity="HIGH",
                                    suggestion=f"實現 {method} 方法",
                                )
                            )

                    # 嘗試執行 audit_operation
                    if hasattr(auditor, "audit_operation"):
                        try:
                            test_data = {
                                "operation_id": "test_001",
                                "type": "validation",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                            result = auditor.audit_operation(test_data)
                            if result is None:
                                violations.append(
                                    Violation(
                                        rule_id="MNGA-AUDITOR-004",
                                        file_path="ecosystem/enforcers/self_auditor.py",
                                        line_number=None,
                                        message="audit_operation 返回 None",
                                        severity="MEDIUM",
                                        suggestion="確保 audit_operation 返回有效的審計結果",
                                    )
                                )
                        except Exception as e:
                            violations.append(
                                Violation(
                                    rule_id="MNGA-AUDITOR-005",
                                    file_path="ecosystem/enforcers/self_auditor.py",
                                    line_number=None,
                                    message=f"audit_operation 執行失敗: {str(e)[:100]}",
                                    severity="HIGH",
                                    suggestion="修復 audit_operation 方法",
                                )
                            )

        except Exception as e:
            violations.append(
                Violation(
                    rule_id="MNGA-AUDITOR-006",
                    file_path="ecosystem/enforcers/self_auditor.py",
                    line_number=None,
                    message=f"無法載入自我審計器: {str(e)[:100]}",
                    severity="CRITICAL",
                    suggestion="修復模組導入錯誤",
                )
            )

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        return EnforcementResult(
            check_name="Self Auditor",
            passed=len([v for v in violations if v.severity == "CRITICAL"]) == 0,
            message=f"自我審計器檢查完成，發現 {len(violations)} 個問題",
            violations=violations,
            files_scanned=1,
            execution_time_ms=int(elapsed),
        )

    def check_mnga_architecture(self) -> EnforcementResult:
        """檢查 MNGA 架構完整性"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        # MNGA 架構定義
        mnga_architecture = {
            # Layer 6: Reasoning
            "ecosystem/reasoning/dual_path/internal": {
                "required_files": [
                    "retrieval.py",
                    "knowledge_graph.py",
                    "index_builder.py",
                ],
                "description": "內部檢索系統",
            },
            "ecosystem/reasoning/dual_path/external": {
                "required_files": ["retrieval.py", "web_search.py", "domain_filter.py"],
                "description": "外部檢索系統",
            },
            "ecosystem/reasoning/dual_path/arbitration": {
                "required_files": ["arbitrator.py", "rule_engine.py"],
                "description": "仲裁系統",
            },
            "ecosystem/reasoning/dual_path/arbitration/rules": {
                "required_files": ["security.yaml", "api.yaml", "dependency.yaml"],
                "description": "仲裁規則庫",
            },
            "ecosystem/reasoning/traceability": {
                "required_files": ["traceability.py", "feedback.py"],
                "description": "溯源系統",
            },
            "ecosystem/reasoning/agents": {
                "required_files": ["planning_agent.py"],
                "description": "智能體系統",
            },
            # Contracts
            "ecosystem/contracts/reasoning": {
                "required_files": [
                    "dual-path-spec.yaml",
                    "arbitration-rules.yaml",
                    "feedback-schema.yaml",
                ],
                "description": "推理合約",
            },
            # Layer 3: Indexes
            "ecosystem/indexes/internal": {
                "required_dirs": ["code-vectors", "docs-index"],
                "description": "內部索引",
            },
            "ecosystem/indexes/external": {
                "required_dirs": ["cache"],
                "description": "外部索引緩存",
            },
            # Platforms
            "platforms/gl.platform-ide/plugins": {
                "required_dirs": ["vscode"],
                "description": "IDE 插件",
            },
            "platforms/gl.platform-assistant/api": {
                "required_files": ["reasoning.py"],
                "description": "推理 API",
            },
            "platforms/gl.platform-assistant/orchestration": {
                "required_files": ["pipeline.py"],
                "description": "編排管道",
            },
        }

        for path, spec in mnga_architecture.items():
            dir_path = self.workspace / path
            files_checked += 1

            # 檢查目錄是否存在
            if not dir_path.exists():
                violations.append(
                    Violation(
                        rule_id="MNGA-ARCH-001",
                        file_path=path,
                        line_number=None,
                        message=f"MNGA 架構目錄缺失: {spec['description']}",
                        severity="HIGH",
                        suggestion=f"創建目錄 {path}",
                    )
                )
                continue

            # 檢查必要文件
            if "required_files" in spec:
                for req_file in spec["required_files"]:
                    file_path = dir_path / req_file
                    files_checked += 1
                    if not file_path.exists():
                        # 檢查 kebab-case 變體
                        kebab_file = req_file.replace("_", "-")
                        if not (dir_path / kebab_file).exists():
                            violations.append(
                                Violation(
                                    rule_id="MNGA-ARCH-002",
                                    file_path=f"{path}/{req_file}",
                                    line_number=None,
                                    message=f"MNGA 架構文件缺失: {spec['description']}",
                                    severity="MEDIUM",
                                    suggestion=f"創建文件 {path}/{req_file}",
                                )
                            )

            # 檢查必要子目錄
            if "required_dirs" in spec:
                for req_dir in spec["required_dirs"]:
                    sub_dir = dir_path / req_dir
                    files_checked += 1
                    if not sub_dir.exists():
                        violations.append(
                            Violation(
                                rule_id="MNGA-ARCH-003",
                                file_path=f"{path}/{req_dir}",
                                line_number=None,
                                message=f"MNGA 架構子目錄缺失: {spec['description']}",
                                severity="MEDIUM",
                                suggestion=f"創建目錄 {path}/{req_dir}",
                            )
                        )

        # 檢查推理組件是否可導入
        reasoning_modules = [
            ("ecosystem.reasoning.dual_path.arbitration.arbitrator", "Arbitrator"),
            (
                "ecosystem.reasoning.dual_path.internal.retrieval",
                "InternalRetrievalEngine",
            ),
            (
                "ecosystem.reasoning.dual_path.external.retrieval",
                "ExternalRetrievalEngine",
            ),
            ("ecosystem.reasoning.traceability.traceability", "TraceabilityEngine"),
        ]

        for module_path, class_name in reasoning_modules:
            files_checked += 1
            try:
                import importlib

                module = importlib.import_module(module_path)
                if not hasattr(module, class_name):
                    violations.append(
                        Violation(
                            rule_id="MNGA-ARCH-004",
                            file_path=module_path.replace(".", "/") + ".py",
                            line_number=None,
                            message=f"類 {class_name} 未在模組中定義",
                            severity="MEDIUM",
                            suggestion=f"在 {module_path} 中定義 {class_name} 類",
                        )
                    )
            except ImportError as e:
                # 模組導入失敗不是關鍵錯誤（可能缺少依賴）
                pass
            except Exception as e:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        # 計算架構完整性
        critical_violations = len([v for v in violations if v.severity == "CRITICAL"])
        high_violations = len([v for v in violations if v.severity == "HIGH"])

        return EnforcementResult(
            check_name="MNGA Architecture",
            passed=critical_violations == 0 and high_violations == 0,
            message=f"檢查 {files_checked} 個架構組件，發現 {len(violations)} 個問題",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def _make_violation(
        self,
        rule_id: str,
        file_path: str,
        message: str,
        severity: str,
        suggestion: str,
        line_number: Optional[int] = None,
    ) -> Violation:
        return Violation(
            rule_id=rule_id,
            file_path=file_path,
            line_number=line_number,
            message=message,
            severity=severity,
            suggestion=suggestion,
        )

    def check_foundation_layer(self) -> EnforcementResult:
        """檢查基礎層組件"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        foundation_modules = [
            "ecosystem/foundation/foundation_dag.py",
            "ecosystem/foundation/format/format_enforcer.py",
            "ecosystem/foundation/language/language_enforcer.py",
        ]

        for module_path in foundation_modules:
            files_checked += 1
            path = self.workspace / module_path
            if not path.exists():
                violations.append(
                    self._make_violation(
                        rule_id="MNGA-FOUNDATION-001",
                        file_path=module_path,
                        line_number=None,
                        message=f"Foundation module not found: {module_path}",
                        severity="MEDIUM",
                        suggestion=f"Create {module_path}",
                    )
                )
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if "@GL-governed" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-FOUNDATION-002",
                            file_path=module_path,
                            line_number=1,
                            message="Missing @GL-governed annotation",
                            severity="LOW",
                            suggestion="Add @GL-governed annotation",
                        )
                    )
            except Exception:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Foundation Layer",
            passed=len(violations) == 0,
            message=f"Scanned {len(foundation_modules)} foundation modules, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_coordination_layer(self) -> EnforcementResult:
        """檢查協調層組件"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        coordination_paths = [
            "ecosystem/coordination/api-gateway",
            "ecosystem/coordination/communication",
            "ecosystem/coordination/data-synchronization",
            "ecosystem/coordination/service-discovery",
        ]

        for coord_path in coordination_paths:
            files_checked += 1
            full_path = self.workspace / coord_path
            if not full_path.exists():
                violations.append(
                    self._make_violation(
                        rule_id="MNGA-COORD-001",
                        file_path=coord_path,
                        line_number=None,
                        message=f"Coordination component not found: {coord_path}",
                        severity="MEDIUM",
                        suggestion=f"Create {coord_path}",
                    )
                )
                continue

            py_files = list(full_path.rglob("*.py"))
            files_checked += len(py_files)
            if not py_files:
                violations.append(
                    self._make_violation(
                        rule_id="MNGA-COORD-002",
                        file_path=coord_path,
                        line_number=None,
                        message="Coordination component has no Python files",
                        severity="LOW",
                        suggestion="Add at least one Python module",
                    )
                )

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Coordination Layer",
            passed=len(violations) == 0,
            message=f"Checked {len(coordination_paths)} coordination components, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_governance_engines(self) -> EnforcementResult:
        """檢查治理引擎"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        governance_engines = [
            (
                "ecosystem/governance/engines/validation/validation_engine.py",
                "ValidationEngine",
            ),
            ("ecosystem/governance/engines/refresh/refresh_engine.py", "RefreshEngine"),
            (
                "ecosystem/governance/engines/reverse-architecture/reverse_architecture_engine.py",
                "ReverseArchitectureEngine",
            ),
            (
                "ecosystem/governance/meta-governance/src/governance_framework.py",
                "GovernanceFramework",
            ),
        ]

        for module_path, class_name in governance_engines:
            files_checked += 1
            path = self.workspace / module_path
            if not path.exists():
                violations.append(
                    self._make_violation(
                        rule_id="MNGA-ENG-001",
                        file_path=module_path,
                        line_number=None,
                        message=f"Governance engine not found: {module_path}",
                        severity="HIGH",
                        suggestion=f"Create {module_path}",
                    )
                )
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if f"class {class_name}" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-ENG-002",
                            file_path=module_path,
                            line_number=None,
                            message=f"Class {class_name} not defined in {module_path}",
                            severity="HIGH",
                            suggestion=f"Define class {class_name}",
                        )
                    )
            except Exception:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Governance Engines",
            passed=len(violations) == 0,
            message=f"Checked {len(governance_engines)} governance engines, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_tools_layer(self) -> EnforcementResult:
        """檢查工具層"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        critical_tools = [
            "ecosystem/tools/scan_secrets.py",
            "ecosystem/tools/fix_security_issues.py",
            "ecosystem/tools/generate_governance_dashboard.py",
            "ecosystem/tools/fact-verification/gov_fact_pipeline.py",
        ]

        for tool_path in critical_tools:
            files_checked += 1
            path = self.workspace / tool_path
            if not path.exists():
                violations.append(
                    self._make_violation(
                        rule_id="MNGA-TOOLS-001",
                        file_path=tool_path,
                        line_number=None,
                        message=f"Critical tool not found: {tool_path}",
                        severity="MEDIUM",
                        suggestion=f"Create {tool_path}",
                    )
                )

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Tools Layer",
            passed=len(violations) == 0,
            message=f"Checked {len(critical_tools)} critical tools, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_events_layer(self) -> EnforcementResult:
        """檢查事件處理層"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        event_emitter_path = "ecosystem/events/event_emitter.py"
        files_checked += 1
        path = self.workspace / event_emitter_path

        if not path.exists():
            violations.append(
                self._make_violation(
                    rule_id="MNGA-EVENTS-001",
                    file_path=event_emitter_path,
                    line_number=None,
                    message=f"Event emitter not found: {event_emitter_path}",
                    severity="HIGH",
                    suggestion=f"Create {event_emitter_path} with EventEmitter",
                )
            )
        else:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if "class EventEmitter" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-EVENTS-002",
                            file_path=event_emitter_path,
                            line_number=None,
                            message="EventEmitter class not defined",
                            severity="HIGH",
                            suggestion="Define EventEmitter class",
                        )
                    )
            except Exception:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Events Layer",
            passed=len(violations) == 0,
            message=f"Checked event layer, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_complete_naming_enforcer(self) -> EnforcementResult:
        """檢查完整命名強制執行器"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        naming_path = "ecosystem/enforcers/complete_naming_enforcer.py"
        files_checked += 1
        path = self.workspace / naming_path

        if not path.exists():
            violations.append(
                self._make_violation(
                    rule_id="MNGA-NAMING-001",
                    file_path=naming_path,
                    line_number=None,
                    message="Complete naming enforcer not found",
                    severity="HIGH",
                    suggestion=f"Create {naming_path}",
                )
            )
        else:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                naming_types = [
                    "CommentNaming",
                    "MappingNaming",
                    "ReferenceNaming",
                    "PathNaming",
                    "PortNaming",
                    "ServiceNaming",
                    "DependencyNaming",
                    "ShortNaming",
                    "LongNaming",
                    "DirectoryNaming",
                    "FileNaming",
                    "EventNaming",
                    "VariableNaming",
                    "EnvironmentVariableNaming",
                    "GitOpsNaming",
                    "HelmReleaseNaming",
                ]
                for naming_type in naming_types:
                    if naming_type not in content:
                        violations.append(
                            self._make_violation(
                                rule_id="MNGA-NAMING-002",
                                file_path=naming_path,
                                line_number=None,
                                message=f"Naming type {naming_type} not implemented",
                                severity="MEDIUM",
                                suggestion=f"Implement {naming_type}",
                            )
                        )
            except Exception:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Complete Naming Enforcer",
            passed=len(violations) == 0,
            message=f"Checked complete naming enforcer, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_enforcers_completeness(self) -> EnforcementResult:
        """檢查強制執行器完整性"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        enforcers = [
            ("ecosystem/enforcers/closed_loop_governance.py", "ClosedLoopGovernance"),
            ("ecosystem/enforcers/pipeline_integration.py", "PipelineIntegration"),
            ("ecosystem/enforcers/role_executor.py", "RoleExecutor"),
            (
                "ecosystem/enforcers/semantic_violation_classifier.py",
                "SemanticViolationClassifier",
            ),
        ]

        for module_path, class_name in enforcers:
            files_checked += 1
            path = self.workspace / module_path
            if not path.exists():
                violations.append(
                    self._make_violation(
                        rule_id="MNGA-ENFORCER-001",
                        file_path=module_path,
                        line_number=None,
                        message=f"Enforcer module not found: {module_path}",
                        severity="MEDIUM",
                        suggestion=f"Create {module_path}",
                    )
                )
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if f"class {class_name}" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-ENFORCER-002",
                            file_path=module_path,
                            line_number=None,
                            message=f"Class {class_name} not defined",
                            severity="MEDIUM",
                            suggestion=f"Define class {class_name}",
                        )
                    )
                if "@GL-governed" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-ENFORCER-003",
                            file_path=module_path,
                            line_number=1,
                            message="Missing @GL-governed annotation",
                            severity="LOW",
                            suggestion="Add @GL-governed annotation",
                        )
                    )
            except Exception:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Enforcers Completeness",
            passed=len(violations) == 0,
            message=f"Checked {len(enforcers)} enforcer modules, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_coordination_services(self) -> EnforcementResult:
        """檢查協調服務"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        services = [
            ("ecosystem/coordination/api-gateway/src/gateway.py", "Gateway"),
            (
                "ecosystem/coordination/communication/src/event_dispatcher.py",
                "EventDispatcher",
            ),
            ("ecosystem/coordination/communication/src/message_bus.py", "MessageBus"),
            (
                "ecosystem/coordination/data-synchronization/src/conflict_resolver.py",
                "ConflictResolver",
            ),
            (
                "ecosystem/coordination/data-synchronization/src/sync_scheduler.py",
                "SyncScheduler",
            ),
            (
                "ecosystem/coordination/service-discovery/src/service_registry.py",
                "ServiceRegistry",
            ),
        ]

        for module_path, class_name in services:
            files_checked += 1
            path = self.workspace / module_path
            if not path.exists():
                violations.append(
                    self._make_violation(
                        rule_id="MNGA-COORD-SVC-001",
                        file_path=module_path,
                        line_number=None,
                        message=f"Coordination service not found: {module_path}",
                        severity="MEDIUM",
                        suggestion=f"Create {module_path}",
                    )
                )
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if f"class {class_name}" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-COORD-SVC-002",
                            file_path=module_path,
                            line_number=None,
                            message=f"Class {class_name} not defined",
                            severity="MEDIUM",
                            suggestion=f"Define class {class_name}",
                        )
                    )
            except Exception:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Coordination Services",
            passed=len(violations) == 0,
            message=f"Checked {len(services)} coordination services, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_meta_governance_systems(self) -> EnforcementResult:
        """檢查元治理系統"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        systems = [
            (
                "ecosystem/governance/meta-governance/src/change_control_system.py",
                "ChangeControlSystem",
            ),
            (
                "ecosystem/governance/meta-governance/src/dependency_manager.py",
                "DependencyManager",
            ),
            (
                "ecosystem/governance/meta-governance/src/impact_analyzer.py",
                "ImpactAnalyzer",
            ),
            (
                "ecosystem/governance/meta-governance/src/review_manager.py",
                "ReviewManager",
            ),
            (
                "ecosystem/governance/meta-governance/src/sha_integrity_system.py",
                "SHAIntegritySystem",
            ),
            (
                "ecosystem/governance/meta-governance/src/strict_version_enforcer.py",
                "StrictVersionEnforcer",
            ),
            (
                "ecosystem/governance/meta-governance/src/version_manager.py",
                "VersionManager",
            ),
        ]

        for module_path, class_name in systems:
            files_checked += 1
            path = self.workspace / module_path
            if not path.exists():
                violations.append(
                    self._make_violation(
                        rule_id="MNGA-META-001",
                        file_path=module_path,
                        line_number=None,
                        message=f"Meta-governance module not found: {module_path}",
                        severity="HIGH",
                        suggestion=f"Create {module_path}",
                    )
                )
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if f"class {class_name}" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-META-002",
                            file_path=module_path,
                            line_number=None,
                            message=f"Class {class_name} not defined",
                            severity="HIGH",
                            suggestion=f"Define class {class_name}",
                        )
                    )
                if "@GL-governed" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-META-003",
                            file_path=module_path,
                            line_number=1,
                            message="Missing @GL-governed annotation",
                            severity="LOW",
                            suggestion="Add @GL-governed annotation",
                        )
                    )
            except Exception:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Meta-Governance Systems",
            passed=len(violations) == 0,
            message=f"Checked {len(systems)} meta-governance modules, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_reasoning_system(self) -> EnforcementResult:
        """檢查推理系統"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        module_path = "ecosystem/reasoning/auto_reasoner.py"
        files_checked += 1
        path = self.workspace / module_path
        if not path.exists():
            violations.append(
                self._make_violation(
                    rule_id="MNGA-REASON-001",
                    file_path=module_path,
                    line_number=None,
                    message="Auto reasoner not found",
                    severity="MEDIUM",
                    suggestion=f"Create {module_path}",
                )
            )
        else:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if "class AutoReasoner" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-REASON-002",
                            file_path=module_path,
                            line_number=None,
                            message="AutoReasoner class not defined",
                            severity="MEDIUM",
                            suggestion="Define AutoReasoner class",
                        )
                    )
            except Exception:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Reasoning System",
            passed=len(violations) == 0,
            message=f"Checked reasoning system, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )

    def check_validators_layer(self) -> EnforcementResult:
        """檢查驗證器層"""
        start_time = datetime.now()
        violations = []
        files_checked = 0

        module_path = "ecosystem/validators/network_validator.py"
        files_checked += 1
        path = self.workspace / module_path
        if not path.exists():
            violations.append(
                self._make_violation(
                    rule_id="MNGA-VALIDATOR-001",
                    file_path=module_path,
                    line_number=None,
                    message="Validator not found",
                    severity="MEDIUM",
                    suggestion=f"Create {module_path}",
                )
            )
        else:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if "class NetworkValidator" not in content:
                    violations.append(
                        self._make_violation(
                            rule_id="MNGA-VALIDATOR-002",
                            file_path=module_path,
                            line_number=None,
                            message="NetworkValidator class not defined",
                            severity="MEDIUM",
                            suggestion="Define NetworkValidator class",
                        )
                    )
            except Exception:
                pass

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        return EnforcementResult(
            check_name="Validators Layer",
            passed=len(violations) == 0,
            message=f"Checked validators, found {len(violations)} issues",
            violations=violations,
            files_scanned=files_checked,
            execution_time_ms=int(elapsed),
        )


# ============================================================================
# 主程序
# ============================================================================


def parse_args():
    """Parse command line arguments"""
    import argparse

    parser = argparse.ArgumentParser(
        description="MNGA Ecosystem Governance Enforcement - 生態系統治理強制執行"
    )
    parser.add_argument(
        "--audit", action="store_true", help="Enable detailed audit logging"
    )
    parser.add_argument(
        "--auto-fix", action="store_true", help="Enable automatic violation remediation"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    parser.add_argument("--output", type=str, help="Output file for audit report")
    parser.add_argument(
        "--strict", action="store_true", help="Strict mode - fail on any violation"
    )

    return parser.parse_args()


def generate_audit_report(results: List[EnforcementResult], args) -> dict:
    """Generate audit report in JSON format"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    all_violations = []
    for result in results:
        all_violations.extend([asdict(v) for v in result.violations])

    total_passed = sum(1 for r in results if r.passed)
    total_failed = len(results) - total_passed

    return {
        "timestamp": timestamp,
        "version": "2.0.0",
        "status": "PASS" if total_failed == 0 else "FAIL",
        "summary": {
            "total_checks": len(results),
            "passed": total_passed,
            "failed": total_failed,
            "total_violations": len(all_violations),
            "critical_violations": len(
                [v for v in all_violations if v.get("severity") == "CRITICAL"]
            ),
            "high_violations": len(
                [v for v in all_violations if v.get("severity") == "HIGH"]
            ),
        },
        "checks": [
            {
                "name": r.check_name,
                "passed": r.passed,
                "message": r.message,
                "files_scanned": r.files_scanned,
                "execution_time_ms": r.execution_time_ms,
                "violations_count": len(r.violations),
            }
            for r in results
        ],
        "violations": all_violations,
        "metadata": {
            "ecosystem_root": str(ECOSYSTEM_ROOT),
            "workspace_root": str(WORKSPACE_ROOT),
            "audit_mode": getattr(args, "audit", False),
            "strict_mode": getattr(args, "strict", False),
        },
    }


def main() -> int:
    """主程序"""
    args = parse_args()

    print_header("🛡️  MNGA 生態系統治理強制執行 v2.0")

    print_info(f"Ecosystem Root: {ECOSYSTEM_ROOT}")
    print_info(f"Workspace Root: {WORKSPACE_ROOT}")

    if args.audit:
        print_info("Audit mode: ENABLED")
    if args.strict:
        print_info("Strict mode: ENABLED")
    if args.dry_run:
        print_info("Dry-run mode: ENABLED")

    # 創建強制執行器
    enforcer = MNGAEnforcer(WORKSPACE_ROOT)

    # 執行所有檢查
    print_step(1, "執行 MNGA 治理檢查...")
    results = enforcer.run_all_checks()

    # 打印結果
    print_header("📊 檢查結果總結")

    print(f"\n{'檢查項目':<25} {'狀態':<10} {'訊息'}")
    print("-" * 70)

    total_passed = 0
    total_failed = 0

    for result in results:
        if result.passed:
            status = f"{Colors.GREEN}✅ PASS{Colors.END}"
            total_passed += 1
        else:
            status = f"{Colors.RED}❌ FAIL{Colors.END}"
            total_failed += 1

        print(f"{result.check_name:<25} {status:<20} {result.message}")

        # 顯示違規詳情
        if result.violations and (args.audit or not result.passed):
            for v in result.violations[:5]:  # 最多顯示 5 個
                severity_color = (
                    Colors.RED
                    if v.severity == "CRITICAL"
                    else Colors.YELLOW if v.severity == "HIGH" else Colors.CYAN
                )
                print(
                    f"  {severity_color}[{v.severity}]{Colors.END} {v.file_path}: {v.message}"
                )
            if len(result.violations) > 5:
                print(f"  ... 還有 {len(result.violations) - 5} 個違規")

    print("=" * 70)

    # 總結
    if total_failed == 0:
        print_success(f"所有檢查通過 ({total_passed}/{len(results)})")
        print_info("生態系統治理合規性: ✅ 完全符合")
    else:
        print_error(f"檢查失敗 ({total_failed}/{len(results)})")
        print_warning("生態系統治理合規性: ❌ 需要修復")

    # 生成審計報告
    if args.audit or args.output:
        report = generate_audit_report(results, args)

        # 保存報告
        reports_dir = WORKSPACE_ROOT / "reports"
        reports_dir.mkdir(exist_ok=True)

        report_file = (
            args.output if args.output else f"audit_report_{report['timestamp']}.json"
        )
        report_path = reports_dir / report_file

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print_info(f"Audit report saved to: {report_path}")

    # JSON 輸出
    if args.json:
        report = generate_audit_report(results, args)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    # 返回碼
    if args.strict:
        # 嚴格模式：任何違規都失敗
        all_violations = sum(len(r.violations) for r in results)
        return 1 if all_violations > 0 else 0
    else:
        # 正常模式：只有關鍵違規才失敗
        return 1 if total_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
