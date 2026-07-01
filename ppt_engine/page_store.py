"""
PPT Component Engine — Page Store
==================================
JSON-backed page library with structured query, search, and CRUD operations.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .schema import PageEntry, PageType


class PageStore:
    """
    Persistent page library backed by a single JSON file.

    Supports:
    - Query by template family, page type, layout variant
    - Full-text search across page metadata
    - CRUD operations with atomic writes
    """

    def __init__(self, path: str | Path | None = None):
        if path is None:
            path = os.path.expanduser("~/.hermes-feishu/skills/ppt/ppt_engine/page_library.json")
        self._path = Path(path)
        self._pages: dict[str, PageEntry] = {}
        self._version: str = "1.0"
        self._total_pages_added: int = 0

        if self._path.exists():
            self._load()

    def __len__(self) -> int:
        return len(self._pages)

    def __bool__(self) -> bool:
        return True

    @property
    def total_pages(self) -> int:
        return len(self._pages)

    @property
    def template_families(self) -> list[str]:
        return sorted(set(p.template_family for p in self._pages.values()))

    def _load(self):
        with open(self._path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._version = data.get("version", "1.0")
        self._total_pages_added = data.get("total_pages_added", 0)
        pages_data = data.get("pages", [])
        self._pages = {}
        for pd in pages_data:
            entry = PageEntry.from_dict(pd)
            self._pages[entry.page_id] = entry

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        data = {
            "version": self._version,
            "total_pages": len(self._pages),
            "total_pages_added": self._total_pages_added,
            "pages": [p.to_dict() for p in self._pages.values()],
        }
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(self._path)

    def add(self, entry: PageEntry) -> str:
        self._pages[entry.page_id] = entry
        self._total_pages_added += 1
        return entry.page_id

    def add_batch(self, entries: list[PageEntry]) -> list[str]:
        ids = []
        for entry in entries:
            self._pages[entry.page_id] = entry
            ids.append(entry.page_id)
        self._total_pages_added += len(entries)
        return ids

    def get(self, page_id: str) -> Optional[PageEntry]:
        return self._pages.get(page_id)

    def remove(self, page_id: str) -> bool:
        if page_id in self._pages:
            del self._pages[page_id]
            return True
        return False

    def remove_family(self, family: str) -> int:
        to_remove = [pid for pid, p in self._pages.items() if p.template_family == family]
        for pid in to_remove:
            del self._pages[pid]
        return len(to_remove)

    def clear(self):
        self._pages.clear()

    def commit(self):
        self._save()

    def query(
        self,
        page_type: PageType | str | None = None,
        template_family: str | None = None,
        min_quality: float = 0.0,
        has_image_slot: bool | None = None,
        has_chart_slot: bool | None = None,
        limit: int = 50,
    ) -> list[PageEntry]:
        if isinstance(page_type, str):
            try:
                page_type = PageType(page_type)
            except ValueError:
                page_type = None

        results = []
        for entry in self._pages.values():
            if page_type is not None and entry.page_type != page_type:
                continue
            if template_family is not None and entry.template_family != template_family:
                continue
            if entry.quality_score < min_quality:
                continue
            if has_image_slot is not None:
                has_img = entry.element_map.image_placeholders > 0
                if has_img != has_image_slot:
                    continue
            if has_chart_slot is not None:
                has_ch = entry.element_map.chart_placeholders > 0
                if has_ch != has_chart_slot:
                    continue
            results.append(entry)

        results.sort(key=lambda e: e.quality_score, reverse=True)
        return results[:limit]

    def search(self, keyword: str, limit: int = 20) -> list[PageEntry]:
        kw = keyword.lower()
        results = []
        for entry in self._pages.values():
            score = 0
            if kw in entry.page_id.lower():
                score += 5
            if kw in entry.page_type.value.lower():
                score += 4
            if kw in entry.template_family.lower():
                score += 3
            for ts in entry.text_structure:
                if kw in ts.role.lower():
                    score += 1
            if score > 0:
                results.append((score, entry))
        results.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in results[:limit]]

    def list_families(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self._pages.values():
            counts[entry.template_family] = counts.get(entry.template_family, 0) + 1
        return dict(sorted(counts.items()))

    def list_types(self, family: str | None = None) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self._pages.values():
            if family is not None and entry.template_family != family:
                continue
            pt = entry.page_type.value
            counts[pt] = counts.get(pt, 0) + 1
        return dict(sorted(counts.items()))

    def stats(self) -> dict:
        return {
            "total_pages": self.total_pages,
            "total_pages_added": self._total_pages_added,
            "template_families": self.list_families(),
            "page_types": self.list_types(),
            "library_path": str(self._path),
        }
