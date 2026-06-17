# 🧭 CursorOS: The Desktop Agentic Overlay
## *A Comprehensive Product & Architecture Report*

> **Status:** v1.2 Stable Implementation
> **Strategic Intent:** Bridging the gap between natural language intent and Windows OS-level automation.

---

## 1. 🌟 Product Vision & Context
**What is CursorOS?**
CursorOS is a high-performance, context-aware AI overlay for the Windows desktop. It exists to solve the "fragmentation of intent" on modern PCs, where users often know *what* they want to do (e.g., "find that invoice from last week and put it in my tax folder") but must manually navigate multiple file systems, search tools, and applications to achieve it.

**Core Mission:**
To transform the desktop from a passive collection of files and folders into an **active, agentic environment** that understands semantic descriptions and automates complex multi-step workflows instantly via a unified global hotkey.

---

## 2. 🔥 Core Value Propositions
1.  **Semantic Retrieval:** Search for files based on *meaning* and *time* (e.g., "the project I worked on last night") rather than just literal filenames.
2.  **Contextual Awareness:** The agent "sees" what you are doing—knowing which Explorer windows are open and which files you've recently touched—to provide relevant assistance.
3.  **Action Chaining:** Moving beyond search to *execution*. CursorOS doesn't just find a file; it can open it, copy its path, summarize its contents, or move it to a logically categorized folder in one step.
4.  **Zero-Latency Interaction:** A lightweight, native overlay that activates instantly (`Ctrl + Shift + Space`) without the overhead of a full browser or heavy application.

---

## 3. 🧠 Technical Architecture

### A. The Multi-LLM "Brain"
CursorOS uses a **Dual-LLM Stack** to ensure maximum reliability and reasoning depth:
*   **Primary Brain:** **Google Gemini (Generative AI)** handles complex planning, semantic expansion of search queries, and file content summarization.
*   **Fallback Brain:** **Groq (Llama-3)** provides high-speed redundancy. If Gemini hits a rate limit or quota, Groq takes over instantly, ensuring the UI never hangs.

### B. The Parallel Retrieval Infrastructure
Unlike traditional search, CursorOS runs a **Tri-Stream Retrieval** process using `concurrent.futures`:
1.  **Windows Index Stream:** Queries the native ADODB Windows Search Index for system-wide performance.
2.  **Context Stream:** Scans active File Explorer windows to prioritize files the user is currently looking at.
3.  **Recent Items Stream:** Monitors the Windows "Recent Files" list to catch the most relevant recent activity.
*   **Dynamic Ranking:** A custom scoring algorithm weights these results based on user intent (e.g., a "find" query prioritizes the index, while an "organize" query prioritizes open folders).

### C. Transactional Execution Layer
For "destructive" actions like moving files, CursorOS implements a **Safety-First Workflow**:
*   **Approval Gate:** The agent generates a "Proposal Tree" (JSON-based plan). The user must confirm this plan in the UI before any file moves.
*   **Atomic Rollback:** If a folder organization fails midway, the system reverse-moves all files to their original locations and cleans up any empty folders created.

---

## 4. 🚀 Current Capability Matrix

| Feature | Description | Tech Stack |
| :--- | :--- | :--- |
| **Global Activation** | Instant toggle via `Ctrl + Shift + Space` with a 500ms debounce. | `keyboard`, `threading` |
| **Advanced Find** | Semantic search with temporal awareness ("last month", "yesterday"). | `ADODB`, `LLM Expansion` |
| **Smart Organize** | AI-driven folder categorization with interactive preview and manual override. | `shutil`, `Agent Planning` |
| **Content Peeking** | Reads text-based files (`.py`, `.md`, `.json`) to answer user questions. | `os.read`, `LLM Summary` |
| **System Tray** | Background persistence and clean application lifecycle management. | `pystray` |
| **Cursor Change** | Experimental: Describe a cursor, AI finds it, downloads, and applies it. | `ctypes`, `winreg` |

---

## 5. 🎨 Design Evolution & Decisions

### The Frontend Pivot (Stable vs. Rich Aesthetics)
*   **The Goal:** To achieve a "Glassmorphism" look using React + Tailwind.
*   **The Challenge:** A migration to `pywebview` was attempted (May 31, 2026) but encountered persistent Windows-level transparency bugs ("White Box") and window management conflicts.
*   **The Decision:** Reverted to **Native Tkinter**.
*   **The Outcome:** We chose **Stability over Style**. However, we successfully back-ported modern features (animations, interactive lists, and scrollable results) into the native Tkinter engine to keep the UI feeling "alive" while maintaining 100% transparency reliability.

---

## 📅 Roadmap: The v2 Vision
1.  **Vision Integration:** Incorporating **OmniParser** to allow the agent to "see" non-file elements on the screen (UI buttons, icons, web content).
2.  **Multimodal Chaining:** Expanding actions to include web search, email drafting, and clipboard-based automation.
3.  **Local Indexing:** Moving beyond Windows Indexing to a vector-based local database for true semantic "long-term memory" of the user's data.

---
*End of Report*
