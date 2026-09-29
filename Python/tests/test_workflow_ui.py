import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from src.ui.layout.body import (
    ACTIVE_STEP_KEY,
    FINGERPRINT_KEY,
    MESSAGES_KEY,
    MODEL_KEY,
    RUN_ID_KEY,
    WORKFLOW_KEY,
    sync_workflow_state,
)


BODY_SCRIPT = """
from src.Workflows.workflow import load_workflows
from src.ui.layout.body import render_body

render_body("ai/test", WORKFLOW_NAME, load_workflows())
"""

FULL_APP_SCRIPT = """
from src.ui.layout.body import render_body
from src.ui.layout.footer import render_footer

selected_model, selected_workflow, workflows, error = render_footer()
if error:
    raise RuntimeError(error)
render_body(selected_model, selected_workflow, workflows)
"""

FOOTER_SCRIPT = """
from src.ui.layout.footer import render_footer

render_footer()
"""


def body_app(workflow_name: str) -> AppTest:
    return AppTest.from_string(
        BODY_SCRIPT.replace("WORKFLOW_NAME", repr(workflow_name)),
        default_timeout=10,
    )


def submit_query(app: AppTest, run_id: int, query: str) -> AppTest:
    app.text_area(key=f"workflow-query-{run_id}").set_value(query)
    return app.button(key=f"workflow-query-submit-{run_id}").click().run()


class WorkflowStateTests(unittest.TestCase):
    def test_selection_fingerprint_initializes_and_resets_run_state(self):
        state = {}

        changed = sync_workflow_state(
            state,
            selected_model="ai/one",
            selected_workflow="Workflow 1",
            step_types=["query-step", "output-step"],
        )

        self.assertTrue(changed)
        self.assertEqual(state[MODEL_KEY], "ai/one")
        self.assertEqual(state[WORKFLOW_KEY], "Workflow 1")
        self.assertEqual(state[ACTIVE_STEP_KEY], 0)
        self.assertEqual(state[MESSAGES_KEY], {})
        self.assertEqual(state[RUN_ID_KEY], 1)

        state[ACTIVE_STEP_KEY] = 2
        state[MESSAGES_KEY] = {0: {"IsError": False, "Message": "stale"}}
        self.assertFalse(
            sync_workflow_state(
                state,
                selected_model="ai/one",
                selected_workflow="Workflow 1",
                step_types=["query-step", "output-step"],
            )
        )
        self.assertIn(0, state[MESSAGES_KEY])

        self.assertTrue(
            sync_workflow_state(
                state,
                selected_model="ai/two",
                selected_workflow="Workflow 1",
                step_types=["query-step", "output-step"],
            )
        )
        self.assertEqual(state[ACTIVE_STEP_KEY], 0)
        self.assertEqual(state[MESSAGES_KEY], {})
        self.assertEqual(state[RUN_ID_KEY], 2)
        self.assertEqual(
            state[FINGERPRINT_KEY],
            ("ai/two", "Workflow 1", ("query-step", "output-step")),
        )


class WorkflowUiTests(unittest.TestCase):
    def test_footer_displays_model_and_default_workflow_selectors(self):
        with patch(
            "src.ui.layout.footer.DockerLLM.list_models",
            return_value=(["ai/one", "ai/two"], None),
        ):
            app = AppTest.from_string(FOOTER_SCRIPT).run()

        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="selected_model").options, ["ai/one", "ai/two"])
        self.assertEqual(
            app.selectbox(key="selected_workflow").options,
            ["Workflow 1", "Workflow 2"],
        )

    def test_workflow_one_renders_two_cards_and_never_calls_llm(self):
        with patch("src.Workflows.workflow.DockerLLM.call") as model_call:
            app = body_app("Workflow 1").run()
            self.assertFalse(app.exception)
            app.get_by_key("workflow-step-active-0")
            app.get_by_key("workflow-step-unstarted-1")
            self.assertFalse(app.text_area(key="workflow-query-1").disabled)
            self.assertEqual(
                [heading.value for heading in app.subheader],
                ["Step 1 · Query", "Step 2 · Output"],
            )
            initial_markdown = [element.value for element in app.markdown]
            self.assertIn("**Input Text**", initial_markdown)
            self.assertIn(":blue-badge[Active]", initial_markdown)
            self.assertIn(":gray-badge[Unstarted]", initial_markdown)

            app = submit_query(app, run_id=1, query="direct output")

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state[ACTIVE_STEP_KEY], 2)
        self.assertEqual(app.session_state[MESSAGES_KEY][1]["Message"], "direct output")
        app.get_by_key("workflow-step-complete-0")
        app.get_by_key("workflow-step-complete-1")
        self.assertEqual(app.text_area(key="workflow-query-1").value, "direct output")
        self.assertTrue(app.text_area(key="workflow-query-1").disabled)
        self.assertTrue(app.button(key="workflow-query-submit-1").disabled)
        completed_markdown = [element.value for element in app.markdown]
        self.assertIn(":green-badge[Complete]", completed_markdown)
        self.assertIn("direct output", completed_markdown)
        model_call.assert_not_called()

    def test_workflow_two_calls_model_once_and_renders_response(self):
        with patch(
            "src.Workflows.workflow.DockerLLM.call",
            return_value=("model response", None),
        ) as model_call:
            app = body_app("Workflow 2").run()
            self.assertFalse(app.exception)
            app.get_by_key("workflow-step-active-0")
            app.get_by_key("workflow-step-unstarted-1")
            app.get_by_key("workflow-step-unstarted-2")
            self.assertEqual(
                [heading.value for heading in app.subheader],
                ["Step 1 · Query", "Step 2 · LLM prompt", "Step 3 · Output"],
            )

            app = submit_query(app, run_id=1, query="ask model")

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state[ACTIVE_STEP_KEY], 3)
        self.assertEqual(app.session_state[MESSAGES_KEY][2]["Message"], "model response")
        app.get_by_key("workflow-step-complete-0")
        app.get_by_key("workflow-step-complete-1")
        app.get_by_key("workflow-step-complete-2")
        self.assertEqual(app.text_area(key="workflow-query-1").value, "ask model")
        self.assertTrue(app.text_area(key="workflow-query-1").disabled)
        self.assertIn("**Response**", [element.value for element in app.markdown])
        self.assertIn("**Output**", [element.value for element in app.markdown])
        self.assertGreaterEqual(
            [element.value for element in app.markdown].count("model response"),
            2,
        )
        model_call.assert_called_once_with("ai/test", "ask model")

    def test_a_new_run_has_exactly_one_active_card_and_completion_has_zero(self):
        app = body_app("Workflow 1").run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state[ACTIVE_STEP_KEY], 0)
        app.get_by_key("workflow-step-active-0")
        app.get_by_key("workflow-step-unstarted-1")

        app = submit_query(app, run_id=1, query="hello")

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state[ACTIVE_STEP_KEY], 2)
        app.get_by_key("workflow-step-complete-0")
        app.get_by_key("workflow-step-complete-1")
        self.assertEqual(app.text_area(key="workflow-query-1").value, "hello")

    def test_model_failure_reaches_output_as_red_error(self):
        with patch(
            "src.Workflows.workflow.DockerLLM.call",
            return_value=(None, "runner unavailable"),
        ):
            app = body_app("Workflow 2").run()
            app = submit_query(app, run_id=1, query="ask model")

        self.assertFalse(app.exception)
        self.assertTrue(app.session_state[MESSAGES_KEY][2]["IsError"])
        self.assertGreaterEqual(len(app.error), 2)
        self.assertEqual(
            app.error[-1].value,
            "The model request failed: runner unavailable",
        )

    def test_workflow_and_model_selector_changes_reset_completed_run(self):
        with (
            patch(
                "src.ui.layout.footer.DockerLLM.list_models",
                return_value=(["ai/one", "ai/two"], None),
            ),
            patch(
                "src.Workflows.workflow.DockerLLM.call",
                return_value=("model response", None),
            ),
        ):
            app = AppTest.from_string(FULL_APP_SCRIPT, default_timeout=10).run()
            app = submit_query(app, run_id=1, query="first run")
            self.assertTrue(app.session_state[MESSAGES_KEY])

            app.selectbox(key="selected_workflow").select("Workflow 2").run()
            self.assertEqual(app.session_state[ACTIVE_STEP_KEY], 0)
            self.assertEqual(app.session_state[MESSAGES_KEY], {})
            self.assertEqual(app.session_state[RUN_ID_KEY], 2)

            app = submit_query(app, run_id=2, query="second run")
            self.assertTrue(app.session_state[MESSAGES_KEY])

            app.selectbox(key="selected_model").select("ai/two").run()

        self.assertFalse(app.exception)
        self.assertEqual(app.session_state[MODEL_KEY], "ai/two")
        self.assertEqual(app.session_state[ACTIVE_STEP_KEY], 0)
        self.assertEqual(app.session_state[MESSAGES_KEY], {})
        self.assertEqual(app.session_state[RUN_ID_KEY], 3)

    def test_new_session_starts_with_a_fresh_run(self):
        first = body_app("Workflow 1").run()
        second = body_app("Workflow 1").run()

        self.assertFalse(first.exception)
        self.assertFalse(second.exception)
        self.assertEqual(first.session_state[RUN_ID_KEY], 1)
        self.assertEqual(second.session_state[RUN_ID_KEY], 1)
        self.assertEqual(second.session_state[ACTIVE_STEP_KEY], 0)
        self.assertEqual(second.session_state[MESSAGES_KEY], {})


if __name__ == "__main__":
    unittest.main()
