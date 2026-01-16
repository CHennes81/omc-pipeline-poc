"""FastAPI route handlers."""
import json
import traceback
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app import models, schemas, seed, ask_templates
from app.config import settings

router = APIRouter()


# Configuration endpoint
@router.get("/config/ask")
def get_ask_config():
    """Get Ask configuration for frontend (NL mode availability)."""
    return {
        "nl_enabled": settings.is_nl_enabled(),
        "dual_mode_ui": settings.ask_dual_mode_ui,
        "default_mode": settings.ask_default_mode
    }


# Import/Seed
@router.post("/import/seed", response_model=schemas.SeedResponse)
def import_seed(request: schemas.SeedRequest, db: Session = Depends(get_db)):
    """Load seed data into the database."""
    try:
        reset = request.mode == "reset_and_seed"
        result = seed.load_seed_sql(db, reset=reset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "seed_error", "message": str(e)}
        )


# Productions
@router.get("/productions", response_model=schemas.ProductionsResponse)
def get_productions(db: Session = Depends(get_db)):
    """Get all productions."""
    productions = db.query(models.Production).all()
    return {"productions": [{"code": p.code, "title": p.title} for p in productions]}


# Shots
@router.get("/shots", response_model=schemas.ShotsResponse)
def get_shots(production_code: str, db: Session = Depends(get_db)):
    """Get all shots for a production with stage information."""
    query = text("""
        SELECT s.shot_code, s.scene, s.description, vs.stage
        FROM shots s
        JOIN productions p ON s.production_id = p.id
        LEFT JOIN v_shot_stage vs ON s.id = vs.shot_id
        WHERE p.code = :production_code
        ORDER BY s.shot_code
    """)
    result = db.execute(query, {"production_code": production_code})
    rows = result.fetchall()

    shots = [
        {"shot_code": row[0], "scene": row[1], "description": row[2], "stage": row[3] or "NEW"}
        for row in rows
    ]
    return {"shots": shots}


@router.get("/shots/{shot_code}", response_model=schemas.ShotDetailResponse)
def get_shot_detail(shot_code: str, production_code: str, db: Session = Depends(get_db)):
    """Get detailed information about a shot."""
    shot = db.query(models.Shot).join(models.Production).filter(
        models.Shot.shot_code == shot_code,
        models.Production.code == production_code
    ).first()

    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "shot_not_found", "message": f"Shot {shot_code} not found"}
        )

    return {"shot": {"shot_code": shot.shot_code, "scene": shot.scene, "description": shot.description}}


@router.get("/shots/{shot_code}/lineage", response_model=schemas.LineageResponse)
def get_shot_lineage(shot_code: str, production_code: str, db: Session = Depends(get_db)):
    """Get lineage chain for a shot."""
    # Get the shot first
    shot = db.query(models.Shot).join(models.Production).filter(
        models.Shot.shot_code == shot_code,
        models.Production.code == production_code
    ).first()

    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "shot_not_found", "message": f"Shot {shot_code} not found"}
        )

    # Get versions with lineage
    # Strategy: Start with latest version (by created_at/id), then recursively follow derived_from backward
    # Order: depth ASC means latest version (depth 0) first, then ancestors in reverse chronological order
    # Safety: Max depth of 20 prevents infinite loops from cycles
    # Note: We find the "latest" by selecting the version with highest created_at, or if tied, highest id
    query = text("""
        WITH RECURSIVE lineage_chain AS (
            -- Anchor: Get the most recent version for this shot (wrapped in subquery to allow ORDER BY/LIMIT)
            -- Order by created_at DESC, then id DESC as tiebreaker to ensure we get the actual latest version
            SELECT v.id, v.version_type, v.derived_from_version_id, 0 as depth
            FROM (
                SELECT v.id, v.version_type, v.derived_from_version_id
                FROM versions v
                JOIN assets a ON v.asset_id = a.id
                WHERE a.shot_id = :shot_id
                ORDER BY v.created_at DESC, v.id DESC
                LIMIT 1
            ) v

            UNION ALL

            -- Recursively follow derived_from backward to ancestors
            SELECT v.id, v.version_type, v.derived_from_version_id, lc.depth + 1
            FROM versions v
            JOIN lineage_chain lc ON v.id = lc.derived_from_version_id
            WHERE lc.depth < 20  -- Cycle protection: max depth limit
        )
        SELECT id, version_type, derived_from_version_id
        FROM lineage_chain
        ORDER BY depth ASC
    """)
    result = db.execute(query, {"shot_id": shot.id})
    rows = result.fetchall()

    chain = [
        {
            "version_id": row[0],
            "version_type": row[1],
            "derived_from": row[2]
        }
        for row in rows
    ]

    return {"shot_code": shot_code, "chain": chain}


@router.get("/shots/{shot_code}/events", response_model=schemas.EventsResponse)
def get_shot_events(shot_code: str, production_code: str, db: Session = Depends(get_db)):
    """Get all events for a shot."""
    shot = db.query(models.Shot).join(models.Production).filter(
        models.Shot.shot_code == shot_code,
        models.Production.code == production_code
    ).first()

    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "shot_not_found", "message": f"Shot {shot_code} not found"}
        )

    events = db.query(models.Event).filter(
        models.Event.shot_id == shot.id
    ).order_by(models.Event.created_at).all()

    return {
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "version_id": e.version_id,
                "package_id": e.package_id,
                "actor": e.actor,
                "tool": e.tool,
                "created_at": e.created_at
            }
            for e in events
        ]
    }


# Assets
@router.get("/assets/{asset_id}/versions", response_model=List[schemas.VersionResponse])
def get_asset_versions(asset_id: UUID, db: Session = Depends(get_db)):
    """Get all versions for an asset."""
    versions = db.query(models.Version).filter(
        models.Version.asset_id == asset_id
    ).order_by(models.Version.created_at).all()

    return [
        {
            "id": v.id,
            "version_type": v.version_type,
            "storage_uri": v.storage_uri,
            "codec": v.codec,
            "container": v.container,
            "fps": float(v.fps) if v.fps else None,
            "timecode_in": v.timecode_in,
            "timecode_out": v.timecode_out,
            "created_at": v.created_at
        }
        for v in versions
    ]


# Versions
@router.get("/versions/{version_id}/lineage", response_model=schemas.LineageResponse)
def get_version_lineage(version_id: UUID, db: Session = Depends(get_db)):
    """Get lineage chain for a version."""
    # Get the version and its shot
    version = db.query(models.Version).filter(models.Version.id == version_id).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "version_not_found", "message": f"Version {version_id} not found"}
        )

    shot = version.asset.shot

    # Build chain backwards from this version
    query = text("""
        WITH RECURSIVE lineage_chain AS (
            SELECT id, version_type, derived_from_version_id, 0 as depth
            FROM versions
            WHERE id = :version_id

            UNION ALL

            SELECT v.id, v.version_type, v.derived_from_version_id, lc.depth + 1
            FROM versions v
            JOIN lineage_chain lc ON v.id = lc.derived_from_version_id
        )
        SELECT id, version_type, derived_from_version_id
        FROM lineage_chain
        ORDER BY depth DESC
    """)
    result = db.execute(query, {"version_id": version_id})
    rows = result.fetchall()

    chain = [
        {
            "version_id": row[0],
            "version_type": row[1],
            "derived_from": row[2]
        }
        for row in rows
    ]

    return {"shot_code": shot.shot_code, "chain": chain}


# Packages
@router.get("/packages", response_model=schemas.PackagesResponse)
def get_packages(production_code: str, db: Session = Depends(get_db)):
    """Get all packages for a production."""
    packages = db.query(models.Package).join(models.Production).filter(
        models.Production.code == production_code
    ).order_by(models.Package.created_at.desc()).all()

    return {
        "packages": [
            {
                "id": p.id,
                "package_type": p.package_type,
                "label": p.label,
                "vendor": p.vendor,
                "created_at": p.created_at
            }
            for p in packages
        ]
    }


@router.get("/packages/{package_id}", response_model=schemas.PackageDetailResponse)
def get_package_detail(package_id: UUID, db: Session = Depends(get_db)):
    """Get package details with members."""
    package = db.query(models.Package).filter(models.Package.id == package_id).first()
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "package_not_found", "message": f"Package {package_id} not found"}
        )

    members = db.query(models.PackageMember).filter(
        models.PackageMember.package_id == package_id
    ).all()

    member_versions = [
        {
            "version_id": m.version.id,
            "version_type": m.version.version_type,
            "storage_uri": m.version.storage_uri
        }
        for m in members
    ]

    return {
        "package": {
            "id": package.id,
            "package_type": package.package_type,
            "label": package.label,
            "vendor": package.vendor,
            "created_at": package.created_at
        },
        "members": member_versions
    }


@router.get("/packages/{package_id}/members", response_model=List[schemas.PackageMemberResponse])
def get_package_members(package_id: UUID, db: Session = Depends(get_db)):
    """Get package members."""
    members = db.query(models.PackageMember).filter(
        models.PackageMember.package_id == package_id
    ).all()

    return [
        {
            "version_id": m.version.id,
            "version_type": m.version.version_type,
            "storage_uri": m.version.storage_uri
        }
        for m in members
    ]


# Ask
@router.post("/ask")
def ask_question(request: schemas.AskRequest, db: Session = Depends(get_db)):
    """Answer a question using deterministic or NL routing.

    Supports two modes:
    - deterministic: Uses keyword-based routing (default, always available)
    - nl: Uses LLM-based intent routing (requires ASK_NL_ENABLED=true)

    Returns AskResponse or AskClarificationResponse depending on routing outcome.
    """
    from app import nl_router, ask_executor

    # Determine mode (default to deterministic for safety)
    mode = request.mode or "deterministic"

    # Check if NL mode is requested but not enabled
    if mode == "nl" and not settings.is_nl_enabled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "nl_mode_disabled",
                "message": "Natural language mode is not enabled",
                "category": "unanswerable_question"
            }
        )

    template_name = None
    error_code = None
    error_category = None
    exception_message = None
    stack_trace = None

    try:
        if mode == "nl":
            # NL routing path
            return _handle_nl_ask(request, db)
        else:
            # Deterministic routing path (existing logic)
            return _handle_deterministic_ask(request, db)

    except HTTPException:
        # Re-raise HTTPExceptions (already logged and formatted)
        raise
    except SQLAlchemyError as e:
        # Database/SQL errors
        error_code = "query_execution_error"
        error_category = "data_retrieval_failure"
        exception_message = str(e)
        stack_trace = traceback.format_exc()

        # Log the failure
        _log_ask_failure(
            production_code=request.production_code,
            question=request.question,
            template_name=template_name,
            error_code=error_code,
            error_category=error_category,
            exception_message=exception_message,
            stack_trace=stack_trace,
            mode=mode,
        )

        # Return 500 with error envelope per Appendix E
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": error_code,
                "message": exception_message,
                "category": error_category,
            }
        )
    except Exception as e:
        # Other internal errors during template execution
        error_code = "template_error"
        error_category = "data_retrieval_failure"
        exception_message = str(e)
        stack_trace = traceback.format_exc()

        # Log the failure
        _log_ask_failure(
            production_code=request.production_code,
            question=request.question,
            template_name=template_name,
            error_code=error_code,
            error_category=error_category,
            exception_message=exception_message,
            stack_trace=stack_trace,
            mode=mode,
        )

        # Return 500 with error envelope per Appendix E
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": error_code,
                "message": exception_message,
                "category": error_category,
            }
        )


def _handle_deterministic_ask(request: schemas.AskRequest, db: Session) -> schemas.AskResponse:
    """Handle deterministic ask using keyword routing."""
    template_name = None

    try:
        # Route question to template
        template_name, params = ask_templates.route_question(request.question)
    except Exception as routing_error:
        # Routing logic itself failed
        error_code = "unsupported_question"
        error_category = "unanswerable_question"
        exception_message = f"Question routing failed: {str(routing_error)}"
        stack_trace = traceback.format_exc()

        # Log the failure
        _log_ask_failure(
            production_code=request.production_code,
            question=request.question,
            template_name=None,
            error_code=error_code,
            error_category=error_category,
            exception_message=exception_message,
            stack_trace=stack_trace,
            mode="deterministic",
        )

        # Return 400 with error envelope per Appendix E
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": error_code,
                "message": exception_message,
                "category": error_category,
            }
        )

    # Check if routing failed (unsupported or ambiguous)
    if not template_name or template_name not in ask_templates.TEMPLATES:
        error_code = "unsupported_question"
        error_category = "unanswerable_question"
        exception_message = "Question could not be mapped to a supported template"

        # Log the failure
        _log_ask_failure(
            production_code=request.production_code,
            question=request.question,
            template_name=None,
            error_code=error_code,
            error_category=error_category,
            exception_message=exception_message,
            stack_trace=None,
            mode="deterministic",
        )

        # Return 400/422 with error envelope per Appendix E
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": error_code,
                "message": exception_message,
                "category": error_category,
            }
        )

    template_func = ask_templates.TEMPLATES[template_name]

    # Add production_code to params if not present
    if "production_code" not in params:
        params["production_code"] = request.production_code

    # Execute template
    result = template_func(db, **params)
    return result


def _handle_nl_ask(request: schemas.AskRequest, db: Session):
    """Handle NL ask using LLM-based intent routing.

    Returns AskResponse or AskClarificationResponse depending on routing outcome.
    """
    from app import nl_router, ask_executor

    # Get router
    router = nl_router.get_router()
    if not router:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "nl_router_unavailable",
                "message": "NL router could not be initialized",
                "category": "internal_error"
            }
        )

    # Determine if this is a clarification attempt
    is_clarification = request.clarification_context is not None

    # Build session context
    session_context = {"production_code": request.production_code}
    if request.clarification_context:
        session_context.update(request.clarification_context)

    # Route question
    routing_result = router.route(
        question=request.question,
        session_context=session_context,
        is_clarification=is_clarification
    )

    # Log NL routing attempt
    _log_nl_routing(
        production_code=request.production_code,
        question=request.question,
        routing_result=routing_result,
        is_clarification=is_clarification
    )

    # Handle routing outcome
    if routing_result.status == nl_router.RoutingStatus.OK:
        # Execute query via AskExecutor
        executor = ask_executor.get_executor()
        params = routing_result.params or {}
        params["production_code"] = request.production_code

        result = executor.execute(db, routing_result.intent_id, params)
        return result

    elif routing_result.status == nl_router.RoutingStatus.NEEDS_CLARIFICATION:
        # Return clarification response
        return schemas.AskClarificationResponse(
            status="needs_clarification",
            user_message=routing_result.user_message or "Could you provide more details?",
            intent_id=routing_result.intent_id,
            confidence=routing_result.confidence,
            missing_params=routing_result.missing_params
        )

    elif routing_result.status == nl_router.RoutingStatus.UNANSWERABLE:
        # Return HTTP 200 with unanswerable response (expected workflow outcome, not an error)
        return schemas.AskUnanswerableResponse(
            status="unanswerable",
            error_code=routing_result.error_code or "unanswerable_question",
            message=routing_result.error_message or "Question could not be mapped to a supported intent",
            intent_id=routing_result.intent_id,
            confidence=routing_result.confidence
        )

    else:  # ERROR
        # Map to internal error
        _log_ask_failure(
            production_code=request.production_code,
            question=request.question,
            template_name=None,
            error_code=routing_result.error_code or "routing_error",
            error_category="data_retrieval_failure",
            exception_message=routing_result.error_message or "NL routing failed",
            stack_trace=None,
            mode="nl",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": routing_result.error_code or "routing_error",
                "message": routing_result.error_message or "NL routing failed",
                "category": "data_retrieval_failure"
            }
        )


def _log_ask_failure(
    production_code: str,
    question: str,
    template_name: Optional[str],
    error_code: str,
    error_category: str,
    exception_message: str,
    stack_trace: Optional[str],
    mode: str = "deterministic",
):
    """Emit structured JSON log line to stdout per Appendix E.5."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": settings.app_env,
        "endpoint": "/api/ask",
        "mode": mode,
        "production_code": production_code,
        "question": question,
        "template": template_name,
        "error_code": error_code,
        "error_category": error_category,
        "exception": exception_message,
    }

    if stack_trace:
        log_entry["stack_trace"] = stack_trace

    # Emit as single-line JSON to stdout (Railway/local dev will capture)
    print(json.dumps(log_entry, ensure_ascii=False))


def _log_nl_routing(
    production_code: str,
    question: str,
    routing_result,
    is_clarification: bool
):
    """Emit structured log for NL routing attempts per Appendix G."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": settings.app_env,
        "endpoint": "/api/ask",
        "mode": "nl",
        "production_code": production_code,
        "question": question,
        "is_clarification": is_clarification,
        "routing_status": routing_result.status,
        "intent_id": routing_result.intent_id,
        "confidence": routing_result.confidence,
        "missing_params": routing_result.missing_params,
        "error_code": routing_result.error_code,
    }

    # Emit as single-line JSON to stdout
    print(json.dumps(log_entry, ensure_ascii=False))


# Advance operations (optional workflow ops)
@router.post("/shots/{shot_code}/ops/publish_dailies", response_model=schemas.AdvanceResponse)
def publish_dailies(shot_code: str, production_code: str, db: Session = Depends(get_db)):
    """Create DAILIES_PROXY version and DAILIES_PUBLISHED event."""
    # Implementation would create version + event
    # For now, return a placeholder
    return {
        "ok": True,
        "event_id": UUID("00000000-0000-0000-0000-000000000000"),
        "message": "Dailies published (placeholder - implement full logic)"
    }


@router.post("/shots/{shot_code}/ops/create_edit_export", response_model=schemas.AdvanceResponse)
def create_edit_export(shot_code: str, production_code: str, db: Session = Depends(get_db)):
    """Create EDIT_EXPORT version and EDIT_EXPORT_CREATED event."""
    return {
        "ok": True,
        "event_id": UUID("00000000-0000-0000-0000-000000000000"),
        "message": "Edit export created (placeholder - implement full logic)"
    }


@router.post("/shots/{shot_code}/ops/deliver_turnover", response_model=schemas.AdvanceResponse)
def deliver_turnover(shot_code: str, production_code: str, db: Session = Depends(get_db)):
    """Add EDIT_EXPORT to TURNOVER package and emit TURNOVER_DELIVERED event."""
    return {
        "ok": True,
        "event_id": UUID("00000000-0000-0000-0000-000000000000"),
        "message": "Turnover delivered (placeholder - implement full logic)"
    }


@router.post("/shots/{shot_code}/ops/archive", response_model=schemas.AdvanceResponse)
def archive_shot(shot_code: str, production_code: str, db: Session = Depends(get_db)):
    """Add highest quality source to ARCHIVE package and emit ARCHIVED event."""
    return {
        "ok": True,
        "event_id": UUID("00000000-0000-0000-0000-000000000000"),
        "message": "Shot archived (placeholder - implement full logic)"
    }
