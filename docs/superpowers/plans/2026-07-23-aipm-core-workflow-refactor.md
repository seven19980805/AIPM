# AI PM Core Workflow Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan. This run is executed inline because no subagent delegation was requested.

**Goal:** Turn AI PM from a large page with loosely connected features into a coherent requirements workspace whose session launch, guided interview, structured requirement state, and document handoff form one reliable workflow.

**Architecture:** Introduce a backend session-launch domain contract derived from persisted session/template state, centralize session serialization, and expose that contract through create/get APIs. On the frontend, move transport and launch-state normalization out of `App.vue`, render a dedicated launch workspace for template and department starts, then progressively extract template/session orchestration behind typed feature modules. Existing SQLite records and API fields remain compatible throughout the migration.

**Tech Stack:** Python 3.13, Flask, SQLite, Vue 3, TypeScript, Vite, Node test runner, Python `unittest`/pytest, Playwright.

---

## Product Principles

- A template launch must immediately explain what is active, what the interview will cover, and the first decision needed.
- Template content is guidance, not confirmed user input; starting from a template must not fabricate conversation history or completion.
- Every empty, loading, error, and recovery state must tell the user what happened and offer a clear next action.
- The interview and the structured model are two views of one workflow, not separate tools.
- Data-source choices are constrained to SQL Server, SAP, and manual Excel/CSV upload unless the user supplies another source.
- Existing sessions, generated documents, and Vibe Coding handoff remain usable during the refactor.

## Task 1: Define The Session Launch Contract

**Files:**
- Create: `app/services/session_launch.py`
- Create: `tests/test_session_launch.py`
- Modify: `app/services/requirement_collector.py`

1. Add failing tests for a guided template launch with no fabricated messages.
2. Assert that the launch contract contains mode, title, description, current question, ordered stages, source details, and reply suggestions.
3. Assert that an ordinary blank session has a lightweight conversation launch rather than template metadata.
4. Implement a pure launch-context builder with deterministic language fallbacks.
5. Expose `RequirementCollectorService.build_session_launch_context`.
6. Run `pytest tests/test_session_launch.py -q`.

## Task 2: Make Session APIs Consistent

**Files:**
- Modify: `app/api.py`
- Modify: `tests/test_session_launch.py`

1. Add failing API tests proving `POST /api/sessions` and `GET /api/sessions/:id` return the same launch contract.
2. Extract one session-detail serializer used by both endpoints.
3. Include `launch_context` without removing or renaming existing fields.
4. Verify template-not-found and ordinary-session behavior remain unchanged.
5. Run the focused API tests.

## Task 3: Create Typed Frontend Boundaries

**Files:**
- Create: `frontend/src/api/http.ts`
- Create: `frontend/src/features/session/sessionLaunch.ts`
- Create: `frontend/src/features/session/sessionLaunch.test.mjs`
- Modify: `frontend/src/types/session.ts`
- Modify: `frontend/src/App.vue`

1. Add failing Node tests for launch-context normalization, fallbacks, and suggested reply extraction.
2. Define `SessionLaunchContext`, stage, suggestion, and source types.
3. Move JSON request/error handling into `api/http.ts`.
4. Implement a pure normalizer so older sessions without `launch_context` still work.
5. Wire session create/load responses through the typed feature module.
6. Run `node --test src/lib/*.test.mjs src/features/**/*.test.mjs`.

## Task 4: Replace The Blank Conversation With A Launch Workspace

**Files:**
- Create: `frontend/src/components/SessionLaunchPanel.vue`
- Modify: `frontend/src/App.vue`

1. Render the active template or department as the primary empty-session signal.
2. Show the first focused question, stage progress, source/template provenance, and concise reply starters.
3. Let a reply starter populate the existing composer without sending automatically.
4. Keep normal blank-chat behavior concise and preserve all existing upload/voice actions.
5. Add accessible focus, keyboard, loading, and narrow-screen states.

## Task 5: Refactor Template And Session Orchestration

**Files:**
- Create: `frontend/src/api/sessions.ts`
- Create: `frontend/src/api/templates.ts`
- Create: `frontend/src/features/templates/templateStart.ts`
- Create: `frontend/src/features/templates/templateStart.test.mjs`
- Modify: `frontend/src/App.vue`

1. Characterize current create/load/delete/template-start behavior with pure tests.
2. Move session and template endpoint calls into typed API modules.
3. Move template start payload construction and mode rules into `templateStart.ts`.
4. Reduce duplicated state assignment with one `applySessionDetail` path.
5. Keep the existing modal, session history, and legacy sessions compatible.

## Task 6: Recompose The Core Workspace

**Files:**
- Create: `frontend/src/components/workspace/WorkspaceHeader.vue`
- Create: `frontend/src/components/workspace/ConversationWorkspace.vue`
- Create: `frontend/src/components/workspace/RequirementInspector.vue`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/components/StructuredRequirementPanel.vue`

1. Extract the top-level workspace regions without changing business behavior.
2. Make conversation, requirement progress, and document readiness read as one continuous flow.
3. Replace decorative empty space with purposeful context, progress, evidence, and next-action surfaces.
4. Preserve the official background imagery as a low-contrast environmental layer, not a content substitute.
5. Verify no nested-card layout, clipped text, or mobile overlap is introduced.

## Task 7: Strengthen Workflow State And Recovery

**Files:**
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/types/session.ts`
- Modify: `app/api.py`
- Modify: `app/services/requirement_collector.py`

1. Make loading, streaming, stale structured-model sync, generation, and handoff states explicit.
2. Preserve typed error details and expose retry actions at the point of failure.
3. Prevent double-start, double-send, and stale-session response races.
4. Confirm document-generation readiness remains based on user-confirmed requirements.

## Task 8: Full Verification

**Files:**
- Modify tests only where a discovered regression needs coverage.

1. Run `.venv-mac/bin/python -m pytest -q`.
2. Run frontend Node tests.
3. Run `npm run build`.
4. Start backend with a temporary SQLite database and the frontend on a free port.
5. Exercise ordinary, department, and template starts in Playwright at desktop and mobile widths.
6. Verify template launch reload, first reply, structured progress, console output, and network failures.
7. Build the Podman/Docker deployment images or at minimum validate both Dockerfiles and compose configuration when a container runtime is unavailable.

## Migration Boundary

This plan deliberately avoids a database migration. `launch_context` is derived from session metadata, template files, and the current structured snapshot, so historical sessions continue to load. Large-file decomposition follows working feature boundaries instead of a broad rewrite: every extraction must preserve behavior and pass the existing suite before the next extraction begins.
