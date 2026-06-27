---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)."
version: 2.3.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint, double-evolution]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
## Word Documents (.doc — OLE2/BIFF format)

> **Critical**: python-docx only handles `.docx` (OOXML). It cannot open old `.doc` files.

Old `.doc` files are OLE2 compound documents. Three extraction paths exist:

### Path A — LibreOffice (preferred if available)

```bash
# If LibreOffice is installed on the system
soffice --headless --convert-to docx --outdir /tmp/ /path/to/file.doc
# Then read the resulting .docx with python-docx
```

### Path B — PowerShell + Word COM (Windows only, requires MS Word installed)

```powershell
# From WSL: call PowerShell to use Windows Word COM
powershell.exe -Command "
$word = New-Object -ComObject Word.Application
$word.Visible = \$false
$doc = $word.Documents.Open('C:\path\to\file.doc')
$doc.SaveAs([ref]'C:\temp\doc_output.txt', [ref]4)
$doc.Close(); $word.Quit()
"
```

> ⚠️ WSL PowerShell cannot access Word COM (ERR: 80040154 CLASSNOTREG) unless Word is registered as a WSL-accessible Windows COM server.

### Path C — olefile + UTF-16LE regex (pure Python, works in WSL/Linux)

```python
import olefile, re

ole = olefile.OleFileIO('/path/to/file.doc')
word_doc = ole.openstream('WordDocument')
data = word_doc.read()

# Word .doc stores text as UTF-16LE
text_utf16 = data.decode('utf-16le', errors='ignore')

# Extract Chinese + CJK punctuation + common chars
pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef，。！？；：""''【】《》、\s\n\r]+')
matches = pattern.findall(text_utf16)
full_text = ''.join(matches)
# Clean excessive whitespace
full_text = re.sub(r'\s+', ' ', full_text).strip()

print(full_text)
```

> Works reliably for Chinese-language .doc files. English-heavy docs may have more noise. Additional streams like `0Table` may contain supplementary content — also UTF-16LE decodeable.

### Decision Guide

| Situation | Recommended Path |
|-----------|-----------------|
| Linux/WSL, no Word | Path C (olefile) |
| Windows with Word installed | Path B (COM) |
| LibreOffice available anywhere | Path A (soffice) |
| Batch processing | Path A if soffice available, else Path C with scripting |

> 📖 **WSL/Windows interop notes**: See `references/wsl-windows-doc-extraction.md` for PowerShell COM limitations, file path mapping, and old .doc metadata interpretation.

---

- For PowerPoint: see the `powerpoint` skill (uses python-pptx)`
