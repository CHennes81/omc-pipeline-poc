"""AskExecutor interface and implementations for deterministic query execution.

This module decouples intent routing (NL or deterministic) from query execution,
per Appendix G requirements.
"""
from typing import Protocol, Dict, Any
from sqlalchemy.orm import Session
from app import ask_templates


class AskExecutor(Protocol):
    """Protocol defining the interface for Ask query execution.

    All executors must implement this interface to ensure consistent
    behavior regardless of routing mechanism (NL or deterministic).
    """

    def execute(self, db: Session, intent_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a query for the given intent with validated parameters.

        Args:
            db: Database session
            intent_id: The intent identifier (maps to template or stored procedure)
            params: Validated parameters for the query

        Returns:
            AskResponse-shaped dictionary with answer, evidence, explanation

        Raises:
            ValueError: If intent_id is not recognized
            Exception: If query execution fails
        """
        ...


class SqlTemplateExecutor:
    """Executes Ask queries using SQL templates defined in ask_templates module.

    This is the Phase 1 implementation. Future implementations will support
    stored procedures while maintaining the same interface.
    """

    def __init__(self):
        """Initialize executor with template registry."""
        self.templates = ask_templates.TEMPLATES

    def execute(self, db: Session, intent_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query using SQL template.

        Args:
            db: Database session
            intent_id: Maps to a template function name in ask_templates
            params: Query parameters (must include production_code)

        Returns:
            Dict with structure: {template, params, answer, evidence, explanation}

        Raises:
            ValueError: If intent_id doesn't map to a known template
        """
        if intent_id not in self.templates:
            raise ValueError(f"Unknown intent_id: {intent_id}")

        template_func = self.templates[intent_id]

        # Ensure production_code is present (required by all templates)
        if "production_code" not in params:
            raise ValueError("production_code is required but missing from params")

        # Execute template
        result = template_func(db, **params)
        return result


# Singleton instance for application use
_executor = SqlTemplateExecutor()


def get_executor() -> SqlTemplateExecutor:
    """Get the global AskExecutor instance."""
    return _executor
