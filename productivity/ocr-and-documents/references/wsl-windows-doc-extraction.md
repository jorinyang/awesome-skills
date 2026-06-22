# WSL + Windows Document Interop Notes

## Accessing Windows Apps from WSL

### PowerShell/COM
```bash
powershell.exe -Command "Get-Process"    # Works: basic invocation
powershell.exe -Command "..."             # Full PS syntax supported
```

**Limitation**: Word COM (`New-Object -ComObject Word.Application`) is a **Windows-only COM server** and is NOT accessible from WSL PowerShell. Error: `80040154 CLASSNOTREG`. This is a WSL interop boundary, not a Word installation issue.

### Finding Windows executables
```bash
find /mnt/c -name "soffice*.exe" 2>/dev/null | head -5   # LibreOffice
find /mnt/c -name "WINWORD*.EXE" 2>/dev/null | head -5   # MS Word
```

These searches can take 3+ minutes across large drives — run with `timeout` or narrow scope.

### File path mapping
| Windows | WSL |
|---------|-----|
| `C:\Users\Aorus\Documents\` | `/mnt/c/Users/Aorus/Documents/` |
| `C:\Program Files\` | `/mnt/c/Program Files/` |

Use `/mnt/c/` prefix for all Windows paths accessed from WSL.

## Old .doc File Metadata (via `file` command)
```
Composite Document File V2 Document
  - Little Endian / Os: Windows
  - Code page: 1200 (Unicode UTF-16LE)
  - Locale ID: 2052 (Chinese PRC)
  - Creating Application: WPS Office / MS Word
  - Total Editing Time, Author, Last Saved By all visible
```

This metadata confirms it's a WPS-created OLE2 .doc, not OOXML .docx.
