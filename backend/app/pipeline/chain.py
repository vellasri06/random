import os
from typing import Any, Dict, List
import json
import re

from pydantic import BaseModel

# LangChain / OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence


def _extract_structured(text: str) -> Dict[str, Any]:
    """Best-effort regex-based fallback if LLM output deviates.
    This provides resilience when the model returns markdown or bullets.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    meeting_title = ""
    date = None
    attendees: List[str] = []
    executive_summary_parts: List[str] = []
    key_decisions: List[str] = []
    action_items: List[Dict[str, str]] = []

    section = None
    for ln in lines:
        lower = ln.lower()
        if "meeting title" in lower:
            section = "title"
            continue
        if lower.startswith("date"):
            section = "date"
            continue
        if "attendees" in lower:
            section = "attendees"
            continue
        if "executive summary" in lower:
            section = "summary"
            continue
        if "key decisions" in lower or lower.startswith("decisions"):
            section = "decisions"
            continue
        if "action items" in lower or lower.startswith("actions"):
            section = "actions"
            continue

        if section == "title":
            meeting_title = ln
        elif section == "date":
            date = ln
        elif section == "attendees":
            attendees.extend([a.strip("- •, ") for a in re.split(r",|•|-", ln) if a.strip()])
        elif section == "summary":
            executive_summary_parts.append(ln)
        elif section == "decisions":
            if ln[0:2] in {"- ", "• ", "* "}:
                key_decisions.append(ln[2:].strip())
            else:
                key_decisions.append(ln)
        elif section == "actions":
            # Try to parse 'Task - Assigned To - Deadline'
            parts = [p.strip() for p in re.split(r"\||-", ln) if p.strip()]
            if len(parts) >= 3:
                action_items.append({"task": parts[0], "assigned_to": parts[1], "deadline": parts[2]})
            elif len(parts) == 2:
                action_items.append({"task": parts[0], "assigned_to": parts[1], "deadline": None})
            elif len(parts) == 1:
                action_items.append({"task": parts[0], "assigned_to": None, "deadline": None})

    executive_summary = " ".join(executive_summary_parts).strip()

    # Reasonable defaults
    if not meeting_title:
        meeting_title = "Meeting"

    return {
        "meeting_title": meeting_title,
        "date": date,
        "attendees": attendees,
        "executive_summary": executive_summary,
        "key_decisions": key_decisions,
        "action_items": action_items,
    }


def _build_llm() -> ChatOpenAI:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    return ChatOpenAI(model=model, temperature=temperature)


def _summarize_chain() -> RunnableSequence:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert meeting assistant. Write concise, clear summaries."),
        ("user", "Summarize the following meeting transcript into a brief executive summary.\n\nTranscript:\n{transcript}"),
    ])
    return prompt | _build_llm() | StrOutputParser()


def _extraction_chain() -> RunnableSequence:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract decisions, action items with assignees and deadlines, attendees and meeting date."),
        ("user", (
            "From the transcript below, identify:\n"
            "- Meeting title if implied\n"
            "- Date if mentioned\n"
            "- Attendees (names)\n"
            "- Key decisions (bulleted)\n"
            "- Action items as a table with columns Task | Assigned To | Deadline\n\n"
            "Return STRICT JSON with keys: meeting_title, date, attendees (array), key_decisions (array), action_items (array of {task, assigned_to, deadline}).\n\n"
            "Transcript:\n{transcript}"
        )),
    ])
    return prompt | _build_llm() | StrOutputParser()


def _formatting_chain() -> RunnableSequence:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Format extracted data into a professional Minutes of Meeting template."),
        ("user", (
            "Using the following JSON data, produce a cleanly formatted MoM in markdown with sections:\n"
            "- Meeting Title\n- Date\n- Attendees\n- Executive Summary\n- Key Decisions Made\n- Action Items (table with Task | Assigned To | Deadline)\n\n"
            "JSON:\n{data}"
        )),
    ])
    return prompt | _build_llm() | StrOutputParser()


async def generate_mom_from_text(transcript: str) -> Dict[str, Any]:
    summarize = _summarize_chain()
    extract = _extraction_chain()
    format_chain = _formatting_chain()

    summary_text = await summarize.ainvoke({"transcript": transcript})

    extracted_raw = await extract.ainvoke({"transcript": transcript})
    try:
        extracted = json.loads(extracted_raw)
    except Exception:
        extracted = _extract_structured(extracted_raw)

    # Ensure required fields exist
    extracted.setdefault("meeting_title", "Meeting")
    extracted.setdefault("date", None)
    extracted.setdefault("attendees", [])
    extracted.setdefault("key_decisions", [])
    extracted.setdefault("action_items", [])

    extracted["executive_summary"] = summary_text

    formatted_markdown = await format_chain.ainvoke({"data": json.dumps(extracted)})
    extracted["formatted_markdown"] = formatted_markdown
    return extracted
