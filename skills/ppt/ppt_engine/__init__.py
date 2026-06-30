"""
PPT Component Engine
=====================
Two-skill pipeline for PPT template deconstruction and cross-template assembly.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

from .schema import (
    PageEntry, PageType, PageContent, ContentOutline,
    HarmonyMode, FillResult, AssemblyPlan,
    LayoutVariant, ElementMap, DesignTokens, TextSlot,
    ContentConstraints, ContentFitResult, ContentIssue,
    MatchResult, ValidationIssue, EngineConfig,
)
from .page_store import PageStore
from .structure_parser import StructureParser
from .template_filler import TemplateFiller, PageMatcher, ContentAnalyzer, SlideAssembler, SlideValidator


class PPTEngine:
    """Main entry point for the PPT Component Engine."""

    def __init__(self, page_library_path=None, harmony_mode=HarmonyMode.KEEP_SOURCE):
        if page_library_path is None:
            page_library_path = os.path.expanduser("~/.hermes-feishu/skills/ppt/ppt_engine/page_library.json")
        self.config = EngineConfig(page_library_path=str(page_library_path), harmony_mode=harmony_mode)
        self.store = PageStore(page_library_path)
        self.parser = StructureParser()
        self.filler = TemplateFiller(self.store)
        self.filler.assembler.harmony_mode = harmony_mode

    def parse_template(self, pptx_path, family_name):
        return self.parser.parse_template(pptx_path, family_name, self.store)

    def parse_templates(self, templates):
        return self.parser.parse_templates(templates, self.store)

    def fill(self, outline, output_path, validate=True, harmony_mode=None, preferred_family=""):
        if not isinstance(outline, ContentOutline):
            outline = ContentOutline.from_dicts(
                outline, title="",
                harmony_mode=harmony_mode or self.config.harmony_mode,
                preferred_family=preferred_family,
            )
        if harmony_mode:
            self.filler.assembler.harmony_mode = harmony_mode
        return self.filler.fill(outline, output_path, validate=validate)

    def stats(self):
        return {
            "engine": {"version": "1.0.0", "page_library_path": self.config.page_library_path,
                       "harmony_mode": self.config.harmony_mode.value},
            "page_library": self.store.stats(),
        }

    def query_pages(self, page_type=None, template_family=None, **kwargs):
        return self.store.query(page_type=page_type, template_family=template_family, **kwargs)

    def search_pages(self, keyword, limit=20):
        return self.store.search(keyword, limit=limit)

    def list_families(self):
        return self.store.list_families()

    def print_report(self):
        print(f"PPT Component Engine v1.0.0")
        print(f"Library: {self.config.page_library_path}")
        print(f"Pages: {self.store.total_pages}")
        print(f"Families: {len(self.store.template_families)}")
        for family, count in self.store.list_families().items():
            print(f"  [{family}] ({count} pages)")
            for pt, cnt in self.store.list_types(family).items():
                print(f"    {pt}: {cnt}")


def _cli():
    if len(sys.argv) < 2:
        print("Usage: python -m ppt_engine <command> [args]")
        print("Commands: parse <template.pptx> <family> | stats | fill <outline.json> <output.pptx> | search <keyword>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "parse":
        if len(sys.argv) < 4:
            print("Usage: python -m ppt_engine parse <template.pptx> <family_name>")
            sys.exit(1)
        engine = PPTEngine()
        entries = engine.parse_template(sys.argv[2], sys.argv[3])
        for e in entries:
            print(f"  [{e.slide_index:02d}] {e.page_type.value:<20s} | {e.layout_variant.arrangement:<25s} | {e.element_map.text_boxes}T {e.element_map.image_placeholders}I")
        print(f"\nDone. {len(entries)} pages added. Total: {engine.stats()['page_library']['total_pages']} pages.")
    elif cmd == "stats":
        PPTEngine().print_report()
    elif cmd == "fill":
        if len(sys.argv) < 4:
            print("Usage: python -m ppt_engine fill <outline.json> <output.pptx>")
            sys.exit(1)
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            outline_data = json.load(f)
        result = PPTEngine().fill(outline_data, sys.argv[3])
        print(result.print_report())
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: python -m ppt_engine search <keyword>")
            sys.exit(1)
        for entry in PPTEngine().search_pages(sys.argv[2]):
            print(f"  {entry.page_id}: {entry.page_type.value} ({entry.template_family})")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    _cli()
