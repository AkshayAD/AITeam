import streamlit as st  # Needed for st.warning/st.error
import re
import json  # Although not used directly, analyst response parsing might involve JSON in future


def parse_associate_tasks(guidance_text):
    """Parse actionable tasks from the Associate's guidance."""

    if not guidance_text:
        return []

    def _parse_task_lines(task_text: str) -> list[str]:
        """Parse individual task lines from a block of text."""
        lines = task_text.strip().splitlines()
        tasks: list[str] = []
        current: list[str] = []
        for line in lines:
            l = line.strip()
            if not l:
                continue

            # Detect the start of a new task
            if l.startswith(('-', '*')):
                if current:
                    tasks.append(' '.join(current).strip())
                    current = []
                l = l[1:].strip()

            if re.match(r"\d+[.)]\s*", l):
                if current:
                    tasks.append(' '.join(current).strip())
                    current = []
                l = re.sub(r"^\d+[.)]\s*", "", l)

            m = re.match(r"(?:\*\*)?Task\s*\d+\s*[:\-]?\s*(.*)", l, re.IGNORECASE)
            if m:
                if current:
                    tasks.append(' '.join(current).strip())
                    current = []
                l = m.group(1).strip()

            l = l.strip('*').strip()
            current.append(l)

        if current:
            tasks.append(' '.join(current).strip())

        return tasks

    formatted_tasks: list[str] = []

    # --- Attempt 1: Extract section headed "Next Analysis Tasks" ---
    section_match = re.search(
        r"(?is)next analysis tasks:?\s*(.*?)(?=\n\s*\d+\.\s*develop narrative:)",
        guidance_text,
    )
    if section_match:
        formatted_tasks = _parse_task_lines(section_match.group(1))

    # --- Attempt 2: Fallback to detecting lines starting with "Task N" ---
    if not formatted_tasks:
        lines = guidance_text.strip().splitlines(keepends=True)
        task_header_pattern = re.compile(
            r"^\s*(?:[-*]|\d+\.)?\s*\**\s*Task\s*\d+[\.-]?\s*\**", re.IGNORECASE
        )
        current_task_block: list[str] = []

        for line in lines:
            if re.search(r"5\.\s*Develop Narrative", line, re.IGNORECASE):
                if current_task_block:
                    formatted_tasks.append("".join(current_task_block).strip())
                break

            line_stripped = line.strip()
            header_match = task_header_pattern.match(line_stripped)

            if header_match:
                if current_task_block:
                    formatted_tasks.append("".join(current_task_block).strip())
                current_task_block = [line]
            elif current_task_block:
                current_task_block.append(line)

        if current_task_block:
            formatted_tasks.append("".join(current_task_block).strip())

        formatted_tasks = [t for t in formatted_tasks if t]

    # --- Final checks & defaults ---
    if not formatted_tasks:
        try:
            st.warning(
                "Could not automatically parse specific tasks from Associate guidance. Please manually define the task below."
            )
        except Exception:
            print(
                "Warning: Could not automatically parse specific tasks from Associate guidance."
            )
        formatted_tasks = ["Manually define task based on guidance above."]

    if "Manually define task below" not in formatted_tasks:
        formatted_tasks.append("Manually define task below")

    seen: set[str] = set()
    unique_formatted_tasks = []
    for task in formatted_tasks:
        if task not in seen:
            seen.add(task)
            unique_formatted_tasks.append(task)

    formatted_tasks = unique_formatted_tasks

    if "Manually define task below" in formatted_tasks:
        formatted_tasks.remove("Manually define task below")
        formatted_tasks.append("Manually define task below")

    return formatted_tasks


def parse_analyst_task_response(response_text):
    """
    Parses the Analyst's response into Approach, Code, Results, and Insights.
    Uses more robust header matching and content extraction.
    """
    if not response_text:
        print("Parsing Error: No response text provided.")
        return {"approach": "Error: No response from Analyst.", "code": "", "results_text": "", "insights": ""}

    headers = {
        "approach": r"^\s*\d*\.?\s*\**approach\**:",
        "code": r"^\s*\d*\.?\s*\**python?\s*code\**:",
        "results_text": r"^\s*\d*\.?\s*\**results\**:",
        "insights": r"^\s*\d*\.?\s*\**key?\s*insights\**:",
    }

    parts = {
        "approach": "2.Could not parse 'approach' section.",
        "code": "Could not parse 'code' section.",
        "results_text": "Could not parse 'results_text' section.",
        "insights": "Could not parse 'insights' section.",
    }

    section_matches = []
    for key, pattern in headers.items():
        for match in re.finditer(pattern, response_text, re.MULTILINE | re.IGNORECASE):
            section_matches.append({"key": key, "start": match.start(), "end": match.end()})

    sorted_sections = sorted(section_matches, key=lambda x: x["start"])

    for i, section_match in enumerate(sorted_sections):
        key = section_match["key"]
        content_start_index = section_match["end"]
        content_end_index = len(response_text)
        if i + 1 < len(sorted_sections):
            content_end_index = sorted_sections[i + 1]["start"]

        content = response_text[content_start_index:content_end_index].strip()
        content = re.sub(r"^\s*\*\*", "", content).strip()
        content = re.sub(r"\*\*\s*$", "", content).strip()

        parts[key] = content

    return parts
