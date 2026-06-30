"""
PPT Component Engine — Data Models
===================================
PageEntry, ContentOutline, AssemblyPlan, FillResult, ValidationIssue
and all supporting enums/dataclasses for the PPT componentization pipeline.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class PageType(str, Enum):
    """L2: Page functional classification (18 types)."""
    COVER = "cover"
    TOC = "toc"
    SECTION_HEADER = "section-header"
    CONTENT_1COL = "content-1col"
    CONTENT_2COL = "content-2col"
    CONTENT_3COL = "content-3col"
    IMAGE_FULL = "image-full"
    IMAGE_LEFT = "image-left"
    IMAGE_RIGHT = "image-right"
    CHART = "chart"
    TABLE = "table"
    QUOTE = "quote"
    TEAM = "team"
    TIMELINE = "timeline"
    COMPARISON = "comparison"
    NUMBERED_LIST = "numbered-list"
    ENDING = "ending"
    BLANK = "blank"
    UNKNOWN = "unknown"


class HarmonyMode(str, Enum):
    """Design harmonization strategy for cross-template assembly."""
    KEEP_SOURCE = "keep_source"       # Each page keeps its own design tokens
    UNIFY_ALL = "unify_all"           # All pages unified to target family tokens
    ADAPTIVE = "adaptive"             # Same-family keep, cross-family partial harmonize


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# ──────────────────────────────────────────────
# Layout & Element Models
# ──────────────────────────────────────────────

@dataclass
class LayoutVariant:
    """L3: Describes the physical arrangement of elements on a slide."""
    arrangement: str = ""
    image_position: str = ""
    text_position: str = ""
    has_title_bar: bool = False
    has_subtitle: bool = False
    column_count: int = 1
    notes: str = ""


@dataclass
class ElementMap:
    """Counts of different element types on a slide."""
    text_boxes: int = 0
    image_placeholders: int = 0
    chart_placeholders: int = 0
    auto_shapes: int = 0
    tables: int = 0
    groups: int = 0
    connectors: int = 0


@dataclass
class DesignTokens:
    """Extracted visual design properties."""
    primary_color: str = ""
    secondary_color: str = ""
    accent_color: str = ""
    font_title: str = ""
    font_body: str = ""
    title_size_pt: float = 0.0
    body_size_pt: float = 0.0
    spacing: str = ""
    incomplete: bool = False


@dataclass
class TextSlot:
    """Describes one text-holding shape and its role."""
    role: str = ""
    position: str = ""
    font_size_pt: float = 0.0
    max_chars: int = 0
    font_name: str = ""
    font_bold: bool = False
    font_color: str = ""
    alignment: str = ""
    shape_name: str = ""
    shape_id: int = 0
    has_text: bool = True


@dataclass
class ContentConstraints:
    """Capacity limits for content fitting."""
    max_title_chars: int = 0
    max_subtitle_chars: int = 0
    max_body_lines: int = 0
    max_body_chars_per_line: int = 0
    requires_image: bool = False
    requires_chart: bool = False
    capacity_notes: str = ""


# ──────────────────────────────────────────────
# Core Entity: PageEntry
# ──────────────────────────────────────────────

@dataclass
class PageEntry:
    """
    The atomic unit of the page library.
    One entry = one slide, fully described for retrieval and assembly.
    """
    page_id: str = ""
    source_template: str = ""
    template_family: str = ""
    slide_index: int = 0
    page_type: PageType = PageType.UNKNOWN
    layout_variant: LayoutVariant = field(default_factory=LayoutVariant)
    element_map: ElementMap = field(default_factory=ElementMap)
    design_tokens: DesignTokens = field(default_factory=DesignTokens)
    text_structure: list = field(default_factory=list)
    content_constraints: ContentConstraints = field(default_factory=ContentConstraints)
    quality_score: float = 1.0
    source_file: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {}
        for k, v in asdict(self).items():
            if isinstance(v, Enum):
                d[k] = v.value
            elif isinstance(v, Path):
                d[k] = str(v)
            else:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "PageEntry":
        pt = data.get("page_type", "unknown")
        data["page_type"] = PageType(pt) if isinstance(pt, str) else PageType.UNKNOWN
        data["layout_variant"] = LayoutVariant(**data.get("layout_variant", {}))
        data["element_map"] = ElementMap(**data.get("element_map", {}))
        data["design_tokens"] = DesignTokens(**data.get("design_tokens", {}))
        data["content_constraints"] = ContentConstraints(**data.get("content_constraints", {}))
        data["text_structure"] = [TextSlot(**s) for s in data.get("text_structure", [])]
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class PageContent:
    """Content specification for one output slide."""
    page_type: PageType = PageType.CONTENT_1COL
    title: str = ""
    subtitle: str = ""
    body: str = ""
    has_image: bool = False
    image_description: str = ""
    has_chart: bool = False
    chart_type: str = ""
    preferred_family: str = ""
    preferred_page_type: str = ""
    notes: str = ""


@dataclass
class ContentOutline:
    """The user's intent: a list of pages with content to fill."""
    pages: list[PageContent] = field(default_factory=list)
    title: str = ""
    harmony_mode: HarmonyMode = HarmonyMode.KEEP_SOURCE
    preferred_family: str = ""

    def __iter__(self):
        return iter(self.pages)

    def __len__(self):
        return len(self.pages)

    @classmethod
    def from_dicts(cls, items: list[dict], **kwargs) -> "ContentOutline":
        pages = []
        for item in items:
            pt_str = item.pop("page_type", "content-1col")
            try:
                pt = PageType(pt_str) if isinstance(pt_str, str) else pt_str
            except ValueError:
                pt = PageType.UNKNOWN
            pages.append(PageContent(page_type=pt, **item))
        return cls(pages=pages, **kwargs)

    @classmethod
    def from_simple_list(cls, types: list[str], **kwargs) -> "ContentOutline":
        pages = []
        for t in types:
            try:
                pt = PageType(t)
            except ValueError:
                pt = PageType.UNKNOWN
            pages.append(PageContent(page_type=pt))
        return cls(pages=pages, **kwargs)


@dataclass
class ContentIssue:
    page_index: int = 0
    field: str = ""
    message: str = ""
    severity: Severity = Severity.WARNING
    current_value: str = ""
    constraint: str = ""


@dataclass
class ContentFitResult:
    score: float = 0.0
    fit_map: dict = field(default_factory=dict)
    issues: list[ContentIssue] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def is_good(self) -> bool:
        return self.score >= 0.8

    @property
    def is_acceptable(self) -> bool:
        return self.score >= 0.5


@dataclass
class MatchResult:
    entry: PageEntry = field(default_factory=PageEntry)
    score: float = 0.0
    content_fit: ContentFitResult = field(default_factory=ContentFitResult)


@dataclass
class AssemblyPlan:
    pages: list[MatchResult] = field(default_factory=list)
    harmony_mode: HarmonyMode = HarmonyMode.KEEP_SOURCE
    preferred_family: str = ""
    warnings: list[str] = field(default_factory=list)

    def __iter__(self):
        return iter(self.pages)

    def __len__(self):
        return len(self.pages)

    @property
    def any_errors(self) -> bool:
        return any(
            any(i.severity == Severity.ERROR for i in p.content_fit.issues)
            for p in self.pages
        )


@dataclass
class ValidationIssue:
    page_index: int = 0
    shape_name: str = ""
    message: str = ""
    severity: Severity = Severity.WARNING
    check: str = ""


@dataclass
class FillResult:
    output_path: str = ""
    passed: bool = False
    summary: str = ""
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def print_report(self) -> str:
        lines = [
            f"{'✅' if self.passed else '⚠️'} {self.summary}",
            f"  输出: {self.output_path}",
            f"  统计: {json.dumps(self.stats, ensure_ascii=False, default=str)}",
        ]
        for issue in self.issues:
            icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.severity.value, "•")
            lines.append(f"  {icon} P{issue.page_index}: {issue.message}")
        return "\n".join(lines)


@dataclass
class EngineConfig:
    page_library_path: str = ""
    harmony_mode: HarmonyMode = HarmonyMode.KEEP_SOURCE
    verbose: bool = False
