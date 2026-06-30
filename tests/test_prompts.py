"""Regression guard for the M.5 Test-2 crash: the Jinja prompt template tree must be
present and the pipeline's `.j2` templates must parse.

Root cause (incident 2026-06-30): `prompts/` was never ported from project_chimera, so
`PromptManager.__init__` raised FileNotFoundError and the daily pipeline died on first
filter. This test fails loudly if the tree goes missing again.
"""

from __future__ import annotations

from ports.prompts.jinja_prompt_manager import PromptManager

# .j2 templates the daily pipeline / vault writer actually render (NOT the Obsidian
# Tpl_*.md, which are Templater files synced to the vault and never Jinja-rendered).
_PIPELINE_TEMPLATES = [
    "chimera_sys/reviewer_zero.j2",
    "chimera_sys/user_profile.j2",
    "tasks/filter_task.j2",
    "tasks/daily_summary.j2",
    "obsidian_tpl/knowledge_node.j2",
    "obsidian_tpl/deep_read_node.j2",
]


def test_prompt_manager_initializes() -> None:
    pm = PromptManager()
    assert pm.template_path.name == "prompts"
    assert pm.template_path.is_dir(), pm.template_path


def test_pipeline_jinja_templates_parse() -> None:
    pm = PromptManager()
    for name in _PIPELINE_TEMPLATES:
        pm.env.get_template(name)  # raises TemplateNotFound / TemplateSyntaxError
