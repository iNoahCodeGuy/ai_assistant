"""Legacy Settings compatibility layer.

This module restores the historical ``Settings`` class expected by tests and
example scripts while delegating to the newer Supabase-focused configuration.
It keeps the public surface area small but predictable:

- Mirrors ``SupabaseSettings`` defaults so production code stays in sync
- Provides sane fallback values for test environments without env vars
- Supports lightweight overrides (e.g., ``Settings(code_index_path=...)``)

Design Principles
-----------------
Defensibility: test runs should never crash because environment variables are
missing. Maintainability: a single source of truth (`SupabaseSettings`) still
drives the real configuration, with this shim offering backwards compatibility.
Portability: callers can construct ``Settings`` with overrides without touching
global state.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict

from src.config.supabase_config import SupabaseConfig, SupabaseSettings, supabase_settings


def _copy_supabase_settings() -> Dict[str, Any]:
	"""Create a shallow copy of attributes from the global settings instance."""

	attrs: Dict[str, Any] = {}
	for key, value in vars(supabase_settings).items():
		# ``supabase_config`` is a dataclass; create a new instance to avoid
		# accidental mutation of the shared global settings.
		if key == "supabase_config" and isinstance(value, SupabaseConfig):
			attrs[key] = replace(value)
		else:
			attrs[key] = value
	return attrs


class Settings(SupabaseSettings):
	"""Backward-compatible configuration object used across tests.

	Defaults mirror ``SupabaseSettings``. If environment variables are missing
	(common in CI), we fall back to deterministic local values so tests can run
	without secrets.
	"""

	def __init__(self, *, skip_validation: bool = True, **overrides: Any) -> None:
		self._initialized_via_fallback = False
		try:
			super().__init__()
		except Exception:
			# Provide deterministic local defaults for test environments.
			self._initialized_via_fallback = True
			self.is_production = False
			self.is_vercel = False
			self.supabase_config = SupabaseConfig(
				url=overrides.get("supabase_url", "http://localhost:54321"),
				service_role_key=overrides.get("supabase_service_role_key", "service-role-test"),
				anon_key=overrides.get("supabase_anon_key"),
			)
			self.openai_api_key = overrides.get("openai_api_key", "sk-test")
			self.openai_model = overrides.get("openai_model", "gpt-4o-mini")
			self.embedding_model = overrides.get("embedding_model", "text-embedding-3-small")
			self.resend_api_key = overrides.get("resend_api_key", "")
			self.twilio_account_sid = overrides.get("twilio_account_sid", "")
			self.twilio_auth_token = overrides.get("twilio_auth_token", "")
			self.twilio_from_number = overrides.get("twilio_from_number", "")
			self.youtube_fight_link = overrides.get(
				"youtube_fight_link",
				"https://www.youtube.com/watch?v=dQw4w9WgXcQ",
			)
		else:
			# Detach from the global singleton so per-instance mutations (tests)
			# do not bleed into application runtime.
			snapshot = _copy_supabase_settings()
			for key, value in snapshot.items():
				setattr(self, key, value)

		# Provide consistent defaults expected by legacy code paths.
		self.disable_auto_rebuild = overrides.get("disable_auto_rebuild", False)
		self.code_index_path = overrides.get(
			"code_index_path", getattr(self, "code_index_path", "vector_stores/code_index")
		)
		self.career_kb_path = overrides.get(
			"career_kb_path", getattr(self, "career_kb_path", "data/career_kb.csv")
		)
		self.api_key = self.openai_api_key

		# Allow callers to override any attribute explicitly.
		for attr, value in overrides.items():
			setattr(self, attr, value)

		if not skip_validation and not self._initialized_via_fallback:
			self.validate_configuration()

	# Public Helpers ---------------------------------------------------------
	def copy(self, **updates: Any) -> "Settings":
		"""Return a cloned settings instance with attribute overrides."""

		payload = {**vars(self), **updates}
		# Remove non-init bookkeeping internals
		payload.pop("_initialized_via_fallback", None)
		payload["skip_validation"] = True
		return Settings(**payload)

	def validate_configuration(self) -> bool:
		"""Skip strict validation when running in fallback mode."""

		if self._initialized_via_fallback:
			return True
		return super().validate_configuration()


__all__ = ["Settings"]
