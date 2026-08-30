import os
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    from supabase import create_client, Client
    HAS_SUPABASE_SDK = True
except ImportError:
    HAS_SUPABASE_SDK = False

class SupabaseService:
    """Service wrapper for Supabase database and storage integration."""

    def __init__(self) -> None:
        self.url: Optional[str] = os.getenv("SUPABASE_URL")
        self.key: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        self.client: Optional[Any] = None

        if HAS_SUPABASE_SDK and self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                print(f"[Supabase] Connected to {self.url}")
            except Exception as e:
                print(f"[Supabase] Initialization failed: {e}")
                self.client = None
        else:
            print("[Supabase] Not configured or SDK missing. Operating in local SQLite mode.")

    @property
    def is_configured(self) -> bool:
        return self.client is not None

    def upload_file(self, bucket: str, destination_path: str, file_bytes: bytes, content_type: str = "image/jpeg") -> Optional[str]:
        if not self.is_configured:
            return None
        try:
            res = self.client.storage.from_(bucket).upload(
                path=destination_path,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            public_url = self.client.storage.from_(bucket).get_public_url(destination_path)
            return public_url
        except Exception as e:
            print(f"[Supabase Storage Error] {e}")
            return None

    def insert_run(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.is_configured:
            return None
        try:
            res = self.client.table("runs").insert(data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"[Supabase DB Error] insert_run: {e}")
            return None

    def insert_detections(self, detections: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        if not self.is_configured or not detections:
            return None
        try:
            res = self.client.table("detections").insert(detections).execute()
            return res.data
        except Exception as e:
            print(f"[Supabase DB Error] insert_detections: {e}")
            return None

    def insert_report(self, report_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.is_configured:
            return None
        try:
            res = self.client.table("reports").insert(report_data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"[Supabase DB Error] insert_report: {e}")
            return None

    def get_all_runs(self) -> List[Dict[str, Any]]:
        if not self.is_configured:
            return []
        try:
            res = self.client.table("runs").select("*").order("created_at", desc=True).execute()
            return res.data or []
        except Exception as e:
            print(f"[Supabase DB Error] get_all_runs: {e}")
            return []

    def get_all_reports(self) -> List[Dict[str, Any]]:
        if not self.is_configured:
            return []
        try:
            res = self.client.table("reports").select("*").order("created_at", desc=True).execute()
            return res.data or []
        except Exception as e:
            print(f"[Supabase DB Error] get_all_reports: {e}")
            return []
