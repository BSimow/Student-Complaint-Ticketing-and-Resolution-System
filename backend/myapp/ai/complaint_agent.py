# ==============================================
# JSON-structured Technical Complaint AI Agent
# ==============================================
from __future__ import annotations
import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from typing import Any, List, Dict
import re
import time
from openai import APIConnectionError, RateLimitError, APIStatusError
import httpx
from functools import lru_cache

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # allow Django to boot for admin/migrations etc.

class AIConfigError(RuntimeError):
    pass

@lru_cache
def get_client():
    if OpenAI is None:
        raise AIConfigError("Package 'openai' is not installed. Run: pip install openai")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIConfigError("OPENAI_API_KEY is missing. Add it to backend/.env")
    return OpenAI(api_key=api_key)

def ai_agent(prompt: str) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content

def for_frontend(text: str) -> dict:
    return {"result": ai_agent(text)}

LLM_TIMEOUT_S = int(os.getenv("LLM_TIMEOUT", "25"))  # 25s hard limit

# For Windows consoles with Arabic/Unicode text
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
# ---- helpers for fallback mapping ----

_CMD_LINE_RE = re.compile(
    r"""^\s*(?:\$|pip(?:3)?\b|python(?:3)?\b|python\s+-m\b|conda\b|git\b|
            npm\b|npx\b|yarn\b|pnpm\b|sudo\b|apt(?:-get)?\b|brew\b|
            curl\b|wget\b|powershell\b|cmd\s+/c\b|set\s+\w+|export\s+\w+|cd\s+)""",
    re.IGNORECASE | re.VERBOSE,
)

_TRIPLE_BLOCK_RE = re.compile(r"```(?:[a-zA-Z]+)?\s*([\s\S]*?)```", re.MULTILINE)
_INLINE_BT_RE   = re.compile(r"`([^`]+)`")

_INLINE_CMD_PATTERNS = [
    re.compile(r"(pip(?:3)?\s+install\s+[A-Za-z0-9_\-\.]+)", re.IGNORECASE),
    re.compile(r"(python(?:3)?\s+-m\s+\S.+)", re.IGNORECASE),
    re.compile(r"(git\s+(?:clone|pull|checkout)\s+\S.+)", re.IGNORECASE),
    re.compile(r"(conda\s+(?:create|install|activate|env\s+create)\s+\S.*)", re.IGNORECASE),
    re.compile(r"(npm\s+(?:install|i)\s+\S.*)", re.IGNORECASE),
    re.compile(r"(yarn\s+(?:add|install)\s+\S.*)", re.IGNORECASE),
    re.compile(r"(pnpm\s+(?:add|install)\s+\S.*)", re.IGNORECASE),
    re.compile(r"(sudo\s+\S.+)", re.IGNORECASE),
    re.compile(r"(apt(?:-get)?\s+install\s+\S.+)", re.IGNORECASE),
    re.compile(r"(brew\s+install\s+\S.+)", re.IGNORECASE),
    re.compile(r"(curl\s+\S.+)", re.IGNORECASE),
    re.compile(r"(wget\s+\S.+)", re.IGNORECASE),
    re.compile(r"(powershell\s+-[A-Za-z]\S*\s+\S.+)", re.IGNORECASE),
    re.compile(r"(cmd\s+/c\s+\S.+)", re.IGNORECASE),
]

def _lines(s: str) -> List[str]:
    return [ln.rstrip("\r") for ln in (s or "").splitlines()]

def _extract_commands_list(code_raw: str) -> List[str]:
    """Extract only real commands from a mixed code/prose block."""
    if not code_raw:
        return []
    candidates: List[str] = []

    # triple blocks
    for block in _TRIPLE_BLOCK_RE.findall(code_raw):
        for ln in _lines(block):
            s = ln.strip()
            if not s:
                continue
            if s.startswith("$"):
                s = s[1:].strip()
            if _CMD_LINE_RE.match(s):
                candidates.append(s)

    # inline backticks
    for inline in _INLINE_BT_RE.findall(code_raw):
        s = inline.strip()
        if s.startswith("$"):
            s = s[1:].strip()
        if _CMD_LINE_RE.match(s) or any(p.search(s) for p in _INLINE_CMD_PATTERNS):
            candidates.append(s)

    # patterns anywhere
    for patt in _INLINE_CMD_PATTERNS:
        for m in patt.findall(code_raw):
            s = m.strip()
            if s.startswith("$"):
                s = s[1:].strip()
            candidates.append(s)

    # whole-line commands
    for ln in _lines(code_raw):
        s = ln.strip()
        if s.startswith("$"):
            s = s[1:].strip()
        if _CMD_LINE_RE.match(s):
            candidates.append(s)

    # dedup
    seen = set(); dedup: List[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c); dedup.append(c)
    return dedup

_STOPWORDS = {
    "the","to","and","of","in","on","for","a","an","with","be","is","are","it","that","this","your","you",
    "if","then","by","as","from","using","use","run","running","check","open","ensure","make","sure"
}

def _tokens(s: str) -> List[str]:
    return [t for t in re.findall(r"[a-z0-9_]+", (s or "").lower()) if t not in _STOPWORDS]

def _best_step_idx_for_cmd(cmd: str, steps_texts: List[str]) -> int | None:
    """Attach command to the most similar step; return None if low confidence."""
    ctoks = set(_tokens(cmd))
    if not ctoks:
        return None
    best_i, best_score = None, 0.0
    for i, step in enumerate(steps_texts):
        stoks = set(_tokens(step))
        if not stoks:
            continue
        inter = len(ctoks & stoks)
        score = inter / max(1, min(len(ctoks), len(stoks)))
        if ("version" in ctoks and "version" in stoks) or ("install" in ctoks and "install" in stoks):
            score += 0.25
        if score > best_score:
            best_i, best_score = i, score
    return best_i if (best_i is not None and best_score >= 0.25) else None


# ==============================================
# 1) Load API key from .env
# ==============================================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)
print("OpenAI Key loaded:", True)

# ==============================================
# 2) JSON schema (as text) + strict system rules
# ==============================================
SYSTEM_PROMPT = (
    "You are an AI teaching assistant for a student helpdesk. "
    "Return STRICT JSON ONLY (no markdown, no extra text). "
    "Follow the JSON schema exactly (keys, types, names).\n"
    "Input text may be in English, Arabic, or dialects (e.g., Egyptian Arabic), or mixed. "
    "Your job is to ALWAYS internally normalize/translate the complaint into English, then reason on that normalized text. "
    "Final JSON output MUST always use English categories, summaries, and keys.\n"
    "\n"
    "Classification rules:\n"
    "- Always determine the root cause of the complaint before assigning a category. "
    "Do not be misled by surface words like 'error', 'system', 'server' unless the cause truly matches a technical category.\n"
    "- If the complaint is NON-TECHNICAL: "
    "  set routing.is_technical=false and steps_to_apply=[]. "
    "  Use one of these categories: 'administrative', 'logistics', 'schedule_issue', 'general_question', 'other_non_technical'.\n"
    "- If the complaint is TECHNICAL: produce BETWEEN 3 AND 6 steps. "
    "  Each step must be ONE clear action. "
    "  If a step requires terminal/CLI commands, put them in step.commands; otherwise, leave step.commands=[]. "
    "  Categories for technical issues (pick the most specific, avoid 'other_technical' unless nothing else fits):\n"
    "    - coding_bug: errors caused by the student's code or logic\n"
    "    - coding_how_to: questions about how to write or implement code/features\n"
    "    - dev_env_tooling: IDE, interpreter, environment setup, dependencies, package installation\n"
    "    - sys_networks: network, server, connectivity, or external API access issues\n"
    "    - data_ml_dl: database queries, data handling, machine learning, deep learning\n"
    "    - theory_concept: conceptual or theoretical programming/CS/ML questions\n"
    "    - other_technical: only if none of the above categories apply\n"
    "\n"
    "Output rules:\n"
    "- Put commands under the matching step, not in solution.code unless a full block is unavoidable.\n"
    "- Keep 'summary' short and student-friendly.\n"
    "- 'verification_checklist' must be concrete actions the student can check.\n"
    "- 'requests_for_more_info' should be [] unless clarifying questions are truly needed.\n"
    "- Use plain ASCII quotes in JSON. Return ONLY the JSON object.\n"
)

# ===== JSON schema the model must follow =====
RESPONSE_SCHEMA = r"""
Return a SINGLE JSON object that matches EXACTLY this schema:

{
  "routing": {
    "is_technical": true,
    "category": "coding_bug | coding_how_to | dev_env_tooling | data_ml_dl | sys_networks | theory_concept | other_technical | non_technical",
    "confidence": 0.0
  },
  "summary": "Short explanation for the student.",
  "steps_to_apply": [
    {
      "text": "One clear action for this step.",
      "commands": ["optional terminal/CLI commands for THIS step (0..N), one per line, no prose"]
    }
  ],
  "verification_checklist": ["bullet checks the student can validate"],
  "requests_for_more_info": ["0..3 questions for the student, or [] if not needed"],
  "solution": {
    "code_language": "bash | python | text | null",
    "code": "OPTIONAL: full code/commands block ONLY IF absolutely needed (prefer step.commands)."
  }
}

Rules:
- Non-technical -> routing.is_technical=false AND steps_to_apply=[]
- Technical -> 3..6 steps, one action per step. If a step needs a command, put it in step.commands.
- No markdown, no backticks around the whole JSON, no commentary—JSON only.
"""
# ==============================================
# 3) Agent function
# ==============================================
def ai_agent(student_complaint: str, *,model: str = "gpt-4o-mini", temperature: float = 0.0, max_tokens: int = 1000) -> dict[str, Any]:
    """
    Takes a student's complaint and returns a structured JSON dict.
    """
    
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=0,             
            max_tokens=max_tokens,
            # Forces the model to emit a single JSON object (no prose)
            response_format={"type": "json_object"},
            messages= [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{RESPONSE_SCHEMA}\n\nStudent complaint:\n{student_complaint}"},
                ],
            # request lower latency
            timeout=30,
        )
        raw = resp.choices[0].message.content
        parsed = json.loads(raw)
        return parsed

    except OpenAIError as api_err:
        return {"error": f"OpenAI API error: {str(api_err)}", "raw": ""}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "raw": ""}


# ---- 4) Main Shaping in UI


def for_frontend(agent_result: dict[str, Any]) -> dict[str, Any]:
    """
    Shapes the model JSON for the UI:
      - Non-technical: hide details; UI will offer Open Ticket
      - Technical: inline each step's commands
        and, if the model dumped commands in solution.code, attach them to the most relevant step.
      - Verify stays separate. Unmatched commands (rare) go to a final code step.
    """
    if "error" in agent_result:
        return {"status": "error", "message": agent_result["error"]}

    routing = agent_result.get("routing") or {}
    is_technical = bool(routing.get("is_technical", True))
    category = routing.get("category")
    summary = agent_result.get("summary", "")
    verify = list(agent_result.get("verification_checklist") or [])
    ask_more = list(agent_result.get("requests_for_more_info") or [])
    steps_in: List[Dict[str, Any]] = list(agent_result.get("steps_to_apply") or [])
    sol = agent_result.get("solution") or {}
    code_raw = (sol.get("code") or "").strip()

    # ---- fallback: if solution.code has commands and some steps lack commands, try to attach them
    if code_raw:
        cmds = _extract_commands_list(code_raw)
        if cmds:
            steps_texts = [ (s.get("text") or "") for s in steps_in ]
            for cmd in cmds:
                idx = _best_step_idx_for_cmd(cmd, steps_texts)
                if idx is not None:
                    steps_in[idx].setdefault("commands", [])
                    # avoid duplicates
                    if cmd not in steps_in[idx]["commands"]:
                        steps_in[idx]["commands"].append(cmd)
                else:
                    # if nothing matches, append as an extra step at the end
                    steps_in.append({"text": "Run the following commands/code:", "commands": [cmd]})

    # ---- merge commands inline for UI
    def _merge_step(step: Dict[str, Any]) -> str:
        text = (step.get("text") or "").strip()
        cmds = [c.strip() for c in (step.get("commands") or []) if c and c.strip()]
        if not cmds:
            return text
        joined = "; ".join(f"`{c}`" for c in cmds)
        if text.lower().startswith("run the following commands/code"):
            # render as a separate final code block later (UI already supports CODE_PREFIX)
            return "Run the following commands/code:\n" + "\n".join(cmds)
        if text.endswith("."):
            return text[:-1] + f" by running {joined}."
        return text + f" by running {joined}."

    steps_out: List[str] = [_merge_step(s) for s in steps_in if (s.get("text") or "").strip()]

    ui = {
        "status": "ok",
        "is_technical": is_technical,
        "category": category,
        "summary": summary,
        "steps": steps_out,
        "verify": verify,
        "ask_more": ask_more,
        "code_language": sol.get("code_language"),
        "code": code_raw or "",
        "ticket_prefill": (
            f"[AI Routing] type={'technical' if is_technical else 'non-technical'}; "
            f"category={category or 'unknown'}\n"
            f"[Summary]\n{summary.strip()}\n"
            f"[Steps]\n" + "\n".join(f"- {s}" for s in steps_out)
        ).strip(),
    }

    if not is_technical:
        ui["summary"] = None
        ui["steps"] = []
        ui["verify"] = []
        ui["code_language"] = None
        ui["code"] = None

    return ui
