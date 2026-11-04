"""Vendor-specific LLM implementations.

This is the ONLY place vendor SDKs may be imported. Each module implements
``app.llm.base.LLMProvider`` and is registered in ``app.llm.factory``.
"""
