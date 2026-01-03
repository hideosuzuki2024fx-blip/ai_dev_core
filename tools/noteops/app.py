from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


from fastapi import Header

def _require_token(x_noteops_token: str | None):
    """
    If NOTEOPS_TOKEN is set, require matching X-NoteOps-Token header.
    If NOTEOPS_TOKEN is empty, allow (local-dev mode).
    NOTE: token is read per-request (no import-time caching).
    """
    token = os.getenv("NOTEOPS_TOKEN", "").strip()
    if token:
        if not x_noteops_token or x_noteops_token.strip() != token:
            raise HTTPException(status_code=401, detail="Unauthorized: missing or invalid X-NoteOps-Token")

Layer = Literal["0_raw", "1_mash", "2_ferment", "3_article"]
Mode = Literal["overwrite", "append"]
LogKind = Literal["critique", "error", "meta"]

def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)

def _discover_repo_top() -> Path:
    """
    Determine git repo top reliably.
    - Prefer: git rev-parse --show-toplevel executed from this file's directory.
    - Fallback: parents[3] (legacy) if git is unavailable.
    """
    here = Path(__file__).resolve().parent
    r = _run(["git", "rev-parse", "--show-toplevel"], cwd=here)
    if r.returncode == 0 and (r.stdout or "").strip():
        return Path(r.stdout.strip()).resolve()
    # fallback (may be wrong if folder depth changes)
    return Path(__file__).resolve().parents[3]

REPO_TOP = _discover_repo_top()

ALLOWED_PREFIXES = [
    "NoteMD/0_raw/",
    "NoteMD/1_mash/",
    "NoteMD/2_ferment/",
    "NoteMD/3_article/",
    "logs/critique/",
    "logs/error/",
    "logs/meta/",
    "persona/",
    "tools/",
    "actions/",
]
ALLOWED_SINGLE_FILES = {".gitattributes", "README.md", "README_NEW.md"}

def _norm_rel(path: str) -> str:
    p = path.replace("\\\\", "/").replace("\\", "/").lstrip("./")
    if p.startswith("/") or re.match(r"^[A-Za-z]:/", p):
        raise ValueError("absolute path is not allowed")
    parts = [x for x in p.split("/") if x not in ("", ".")]
    if any(x == ".." for x in parts):
        raise ValueError("parent traversal '..' is not allowed")
    return "/".join(parts)

def _is_allowed(rel: str) -> bool:
    if rel in ALLOWED_SINGLE_FILES:
        return True
    return any(rel.startswith(pref) for pref in ALLOWED_PREFIXES)

def _to_abs(rel: str) -> Path:
    return (REPO_TOP / rel).resolve()

def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _write_text_utf8_lf(p: Path, content: str, mode: Mode) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    if mode == "append" and p.exists():
        existing = p.read_text(encoding="utf-8", errors="replace")
        existing = existing.replace("\r\n", "\n").replace("\r", "\n")
        content = existing + content
    p.write_text(content, encoding="utf-8", newline="\n")

def _run_git(args: list[str]) -> str:
    r = _run(["git", *args], cwd=REPO_TOP)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout or "").strip() or "git failed"
        raise RuntimeError(msg)
    return (r.stdout or "").strip()

def _ensure_allowed_path(rel: str) -> str:
    rel_n = _norm_rel(rel)
    if not _is_allowed(rel_n):
        raise HTTPException(status_code=403, detail=f"path not allowed: {rel_n}")
    abs_p = _to_abs(rel_n)
    try:
        abs_p.relative_to(REPO_TOP)
    except Exception:
        raise HTTPException(status_code=403, detail="resolved path escapes repo")
    return rel_n

app = FastAPI(title=APP_TITLE, version="0.2.0")

class RepoStatus(BaseModel):
    topLevel: str
    branch: str
    isClean: bool
    porcelain: str

@app.get("/repo/status", response_model=RepoStatus)
def repo_status():
    try:
        top = _run_git(["rev-parse", "--show-toplevel"])
        branch = _run_git(["branch", "--show-current"])
        porcelain = _run_git(["status", "--porcelain"])
        return RepoStatus(topLevel=top, branch=branch, isClean=(porcelain.strip() == ""), porcelain=porcelain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/repo/status failed: {e}")

@app.get("/debug/repo")
def debug_repo():
    # helps diagnose REPO_TOP mismatch quickly
    return {"tokenEnabled": bool(os.getenv("NOTEOPS_TOKEN","").strip()), "repoTop": str(REPO_TOP),
        "cwd": os.getcwd(),
        "appFile": str(Path(__file__).resolve()),
        "gitTopCheck": _run(["git","rev-parse","--show-toplevel"], cwd=REPO_TOP).stdout.strip()
    }

class NoteWriteIn(BaseModel):
    layer: Layer
    path: str = Field(..., description="Relative path under NoteMD/<layer>/...")
    content: str
    mode: Optional[Mode] = "overwrite"

class NoteWriteOut(BaseModel):
    writtenPath: str
    sha256Before: Optional[str] = None
    sha256After: str

@app.post("/note/write", response_model=NoteWriteOut)
def note_write(inp: NoteWriteIn, x_noteops_token: str | None = Header(default=None)):
    rel = _ensure_allowed_path(f"NoteMD/{inp.layer}/{_norm_rel(inp.path)}")
    abs_p = _to_abs(rel)
    sha_before = _sha256_file(abs_p) if abs_p.exists() else None
    _write_text_utf8_lf(abs_p, inp.content, inp.mode or "overwrite")
    sha_after = _sha256_file(abs_p)
    return NoteWriteOut(writtenPath=rel, sha256Before=sha_before, sha256After=sha_after)

class LogAppendIn(BaseModel):
    kind: LogKind
    path: str = Field(..., description="Relative path under logs/<kind>/...")
    content: str
    mode: Optional[Mode] = "append"

@app.post("/log/append")
def log_append(inp: LogAppendIn, x_noteops_token: str | None = Header(default=None)):
    rel = _ensure_allowed_path(f"logs/{inp.kind}/{_norm_rel(inp.path)}")
    abs_p = _to_abs(rel)
    _write_text_utf8_lf(abs_p, inp.content, inp.mode or "append")
    return {"tokenEnabled": bool(os.getenv("NOTEOPS_TOKEN","").strip()), "ok": True, "writtenPath": rel}

class NormalizeIn(BaseModel):
    root: Optional[str] = "."

@app.post("/normalize/run")
def normalize_run(inp: NormalizeIn, x_noteops_token: str | None = Header(default=None)):
    script = REPO_TOP / "tools" / "normalize-utf8lf.ps1"
    if script.exists():
        root = inp.root or "."
        r = _run(["powershell","-ExecutionPolicy","Bypass","-File",str(script),"-Root",root], cwd=REPO_TOP)
        if r.returncode != 0:
            raise HTTPException(status_code=500, detail=(r.stderr or r.stdout or "normalize failed").strip())
        return {"tokenEnabled": bool(os.getenv("NOTEOPS_TOKEN","").strip()), "ok": True, "method": "powershell", "output": (r.stdout or "").strip()}
    return {"tokenEnabled": bool(os.getenv("NOTEOPS_TOKEN","").strip()), "ok": True, "method": "noop", "output": "tools/normalize-utf8lf.ps1 not found"}

class GitCommitIn(BaseModel):
    message: str
    ayase_approve: bool
    amy_approve: bool
    decision_ref: str

class GitCommitOut(BaseModel):
    committed: bool
    commitSha: Optional[str] = None
    rejectedReason: Optional[str] = None

def _stage_allowlisted():
    for t in ["NoteMD","logs","persona","tools","actions",".gitattributes","README.md","README_NEW.md"]:
        try:
            _run_git(["add","--",t])
        except Exception:
            pass

@app.post("/git/commit", response_model=GitCommitOut)
def git_commit(inp: GitCommitIn, x_noteops_token: str | None = Header(default=None)):
    if not (inp.ayase_approve and inp.amy_approve):
        return GitCommitOut(committed=False, rejectedReason="Governance gate: requires ayase_approve=true AND amy_approve=true")
    if not RE_COMMIT_PREFIX.match(inp.message.strip()):
        return GitCommitOut(committed=False, rejectedReason="Commit message must start with Draft:/Review:/Final:")

    try:
        decision_rel = _ensure_allowed_path(inp.decision_ref)
    except HTTPException:
        return GitCommitOut(committed=False, rejectedReason="decision_ref must be an allowed path (expected logs/critique/...)")
    if not decision_rel.startswith("logs/critique/"):
        return GitCommitOut(committed=False, rejectedReason="decision_ref must be under logs/critique/")
    if not _to_abs(decision_rel).exists():
        return GitCommitOut(committed=False, rejectedReason="decision_ref file does not exist")

    try:
        _stage_allowlisted()
        porcelain = _run_git(["status","--porcelain"])
        if porcelain.strip() == "":
            return GitCommitOut(committed=False, rejectedReason="No changes to commit")
        _run_git(["commit","-m",inp.message])
        sha = _run_git(["rev-parse","HEAD"])
        return GitCommitOut(committed=True, commitSha=sha)
    except Exception as e:
        return GitCommitOut(committed=False, rejectedReason=str(e))

def main():
    import uvicorn
    uvicorn.run("app:app", host=DEFAULT_HOST, port=DEFAULT_PORT, reload=False)

if __name__ == "__main__":
    main()

