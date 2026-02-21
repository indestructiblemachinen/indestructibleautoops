"""Workflow management endpoints for the GovOps Platform API.

Provides endpoints to trigger governance analysis cycles, monitor their
progress, cancel running cycles, and inspect the workflow engine status.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = structlog.get_logger("govops.workflows")

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class TriggerCycleRequest(BaseModel):
    """Request body to trigger a new governance analysis cycle."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ..., min_length=1, max_length=200, description="Human-readable cycle name."
    )
    description: str = Field(default="", max_length=2000, description="Cycle description.")
    modules: list[str] = Field(
        default_factory=list, description="Module IDs to include; empty means all."
    )
    auto_enforce: bool = Field(
        default=False,
        description="Automatically enforce findings above the severity threshold.",
    )
    severity_threshold: str = Field(
        default="warning",
        description="Minimum severity that triggers enforcement: info | warning | error | critical.",
    )
    max_duration_seconds: int = Field(
        default=3600, ge=60, le=86400, description="Maximum cycle duration in seconds."
    )
    tags: dict[str, str] = Field(default_factory=dict, description="Arbitrary tags for filtering.")

    @field_validator("severity_threshold")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        allowed = {"info", "warning", "error", "critical"}
        normalised = v.lower().strip()
        if normalised not in allowed:
            raise ValueError(f"Severity must be one of: {', '.join(sorted(allowed))}")
        return normalised


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class CycleSummary(BaseModel):
    """Compact governance cycle representation for list views."""

    model_config = ConfigDict(from_attributes=True)

    cycle_id: str
    name: str
    status: str
    modules_total: int = 0
    modules_completed: int = 0
    findings_count: int = 0
    enforcements_count: int = 0
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class CycleDetail(CycleSummary):
    """Full governance cycle with configuration and timing metadata."""

    description: str = ""
    auto_enforce: bool = False
    severity_threshold: str = "warning"
    tags: dict[str, str] = Field(default_factory=dict)
    duration_seconds: float | None = None
    scan_report_ids: list[str] = Field(
        default_factory=list, description="Associated scan report IDs."
    )


class CycleTriggerResponse(BaseModel):
    """Response returned when a cycle is successfully queued."""

    cycle_id: str
    status: str = "pending"
    message: str = "Governance cycle queued successfully."


class CycleCancelResponse(BaseModel):
    """Response returned when a cycle cancellation is requested."""

    cycle_id: str
    status: str = "cancelled"
    message: str = "Cycle cancellation requested."


class PaginatedCyclesResponse(BaseModel):
    """Paginated list of governance cycles."""

    items: list[CycleSummary] = Field(default_factory=list)
    total: int = Field(ge=0)
    skip: int = Field(ge=0)
    limit: int = Field(ge=1)
    has_next: bool = False


class WorkflowEngineStatus(BaseModel):
    """Current status of the workflow engine."""

    engine_status: str = Field(description="Engine state: running | paused | stopped.")
    active_cycles: int = Field(default=0, ge=0, description="Number of currently active cycles.")
    queued_cycles: int = Field(default=0, ge=0, description="Number of cycles waiting to execute.")
    completed_today: int = Field(
        default=0, ge=0, description="Cycles completed in the last 24 hours."
    )
    failed_today: int = Field(default=0, ge=0, description="Cycles failed in the last 24 hours.")
    workers_available: int = Field(default=0, ge=0, description="Number of idle worker slots.")
    workers_total: int = Field(default=0, ge=0, description="Total worker capacity.")
    uptime_seconds: float = Field(default=0.0, ge=0, description="Engine uptime in seconds.")
    last_cycle_at: datetime | None = Field(
        default=None, description="Timestamp of the most recently completed cycle."
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/cycles",
    response_model=CycleTriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger analysis cycle",
    description="Queue a new governance analysis cycle for asynchronous execution.",
)
async def trigger_cycle(body: TriggerCycleRequest) -> CycleTriggerResponse:
    """Accept a governance cycle request and enqueue it for processing."""
    cycle_id = str(uuid.uuid4())
    logger.info(
        "cycle_triggered",
        cycle_id=cycle_id,
        name=body.name,
        modules_count=len(body.modules),
        auto_enforce=body.auto_enforce,
    )

    # Placeholder — in production this enqueues via the workflow engine
    return CycleTriggerResponse(
        cycle_id=cycle_id,
        status="pending",
        message=f"Governance cycle '{body.name}' queued successfully.",
    )


@router.get(
    "/cycles",
    response_model=PaginatedCyclesResponse,
    status_code=status.HTTP_200_OK,
    summary="List cycles",
    description="Returns a paginated list of governance analysis cycles.",
)
async def list_cycles(
    skip: int = Query(default=0, ge=0, description="Number of items to skip."),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum items to return."),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by cycle status (pending, running, completed, failed, cancelled).",
    ),
) -> PaginatedCyclesResponse:
    """List governance cycles with pagination and optional status filter."""
    logger.info(
        "cycles_list_requested",
        skip=skip,
        limit=limit,
        status_filter=status_filter,
    )

    # Placeholder — in production this queries the cycle repository
    return PaginatedCyclesResponse(
        items=[],
        total=0,
        skip=skip,
        limit=limit,
        has_next=False,
    )


@router.get(
    "/status",
    response_model=WorkflowEngineStatus,
    status_code=status.HTTP_200_OK,
    summary="Workflow engine status",
    description="Returns the current operational status of the workflow engine.",
)
async def get_workflow_status() -> WorkflowEngineStatus:
    """Return the current state of the workflow engine."""
    logger.info("workflow_status_requested")

    # Placeholder — in production this queries the engine orchestrator
    return WorkflowEngineStatus(
        engine_status="running",
        active_cycles=0,
        queued_cycles=0,
        completed_today=0,
        failed_today=0,
        workers_available=4,
        workers_total=4,
        uptime_seconds=0.0,
        last_cycle_at=None,
    )


@router.get(
    "/cycles/{cycle_id}",
    response_model=CycleDetail,
    status_code=status.HTTP_200_OK,
    summary="Get cycle status",
    description="Returns the full detail of a specific governance cycle.",
    responses={404: {"description": "Cycle not found."}},
)
async def get_cycle(
    cycle_id: str = Path(..., description="UUID of the governance cycle."),
) -> CycleDetail:
    """Retrieve a single governance cycle by its identifier."""
    logger.info("cycle_detail_requested", cycle_id=cycle_id)

    try:
        uuid.UUID(cycle_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid cycle ID format: {cycle_id}",
        )

    # Placeholder — in production this fetches from the cycle repository
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Governance cycle {cycle_id} not found.",
    )


@router.post(
    "/cycles/{cycle_id}/cancel",
    response_model=CycleCancelResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel a cycle",
    description="Request cancellation of a running or queued governance cycle.",
    responses={
        404: {"description": "Cycle not found."},
        409: {"description": "Cycle cannot be cancelled (already completed/failed)."},
    },
)
async def cancel_cycle(
    cycle_id: str = Path(..., description="UUID of the governance cycle to cancel."),
) -> CycleCancelResponse:
    """Request cancellation of a governance cycle.

    Only cycles in ``pending`` or ``running`` status can be cancelled.
    """
    logger.info("cycle_cancel_requested", cycle_id=cycle_id)

    try:
        uuid.UUID(cycle_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid cycle ID format: {cycle_id}",
        )

    # Placeholder — in production this signals the workflow engine
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Governance cycle {cycle_id} not found.",
    )
