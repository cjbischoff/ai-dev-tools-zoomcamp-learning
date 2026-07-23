# Module 1 — AI-Native Developer Workflow

Upstream materials: https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/tree/main/01-overview
(2026 module page is a draft; content may change before Aug 31, 2026.)

## What the Module Teaches

Workflow over tools: what you give an agent before it starts, how you steer it while it runs, how you verify what comes back. Build vehicle is a meeting cost calculator, but the deliverable is the workflow itself.

Lesson arc (11 lessons):

1. Introduction
2. The Tool Map — five categories of AI dev tools; pick one for the cohort
3. Specs Before Code — talk the design through, then write it down
4. Bootstrapping a Project — spec into repo plus task backlog
5. Context Engineering — the `AGENTS.md` every session starts from
6. Grooming a Task — raw backlog item into acceptance criteria
7. Implementing a Task — code against those criteria
8. Testing a Task — verify from a session that did not write the code
9. Loop Engineering — `/goal`, running the agent repeatedly
10. Graph Engineering — PM / engineer / QA as separate agents working one backlog
11. Wrap-up

## Homework 1 (2026): Django TODO App

Build a Django TODO app with an AI tool (no Django knowledge required). Features: create/edit/delete TODOs, due dates, mark resolved. Recommended stack: Python + `uv`, agent-mode IDE assistant.

Steps mirror the six graded questions:

- [ ] Q1: Install Django (record the install command AI suggests)
- [ ] Q2: Create project + app; note which file registers the app in the project
- [ ] Q3: Define models; note the next step after models
- [ ] Q4: Implement TODO logic; note which file holds it
- [ ] Q5: Create `base.html` + `home.html`; note where the template directory is registered
- [ ] Q6: AI-generated tests — review scenarios, run them; note the test command
- [ ] Run with `python manage.py runserver`, iterate until it works
- [ ] Push code to GitHub in a folder like `01-todo/`, submit folder link

Submission form: https://courses.datatalks.club/ai-dev-tools-2025/homework/hw1

## Homework Code Location

Homework code goes in `01-overview/01-todo/` in this repo (repo needs a GitHub remote before submission).
