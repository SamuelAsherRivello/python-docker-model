import unittest
from unittest.mock import patch
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.Workflows.workflow import WorkflowConfigurationError
from src.ui.app import MODEL_UNAVAILABLE_MESSAGE
from src.ui.layout.body import (
    ACTIVE_STEP_KEY,
    FINGERPRINT_KEY,
    MESSAGES_KEY,
    MODEL_KEY,
    RUN_ID_KEY,
    WORKFLOW_KEY,
    reset_workflow_state,
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

footer_state = render_footer()
if footer_state.fatal_error:
    raise RuntimeError(footer_state.fatal_error)
render_body(
    footer_state.selected_model,
    footer_state.selected_workflow,
    footer_state.workflows,
)
"""

FOOTER_SCRIPT = """
import streamlit as st
from src.ui.layout.footer import render_footer

footer_state = render_footer()
st.session_state["footer_test_state"] = {
    "model_available": footer_state.model_available,
    "model_diagnostic": footer_state.model_diagnostic,
    "fatal_error": footer_state.fatal_error,
}
"""

APP_SCRIPT = """
from src.ui.app import render_app

render_app()
"""

PROJECT_ROOT = Path(__file__).parents[1]


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

    def test_reset_workflow_state_preserves_unrelated_values(self):
        state = {
            ACTIVE_STEP_KEY: 1,
            FINGERPRINT_KEY: ("ai/test", "Workflow 1", ("query-step",)),
            MESSAGES_KEY: {0: {"IsError": False, "Message": "stale"}},
            MODEL_KEY: "ai/test",
            RUN_ID_KEY: 7,
            WORKFLOW_KEY: "Workflow 1",
            "workflow-query-7": "stale query",
            "unrelated": "keep me",
        }

        reset_workflow_state(state)

        self.assertEqual(state, {"unrelated": "keep me"})


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
        self.assertTrue(app.session_state["footer_test_state"]["model_available"])
        self.assertIsNone(app.session_state["footer_test_state"]["fatal_error"])

    def test_footer_represents_model_unavailability_without_a_fatal_error(self):
        with patch(
            "src.ui.layout.footer.DockerLLM.list_models",
            return_value=([], "docker command failed with private host details"),
        ):
            app = AppTest.from_string(FOOTER_SCRIPT).run()

        self.assertFalse(app.exception)
        state = app.session_state["footer_test_state"]
        self.assertFalse(state["model_available"])
        self.assertIn("private host details", state["model_diagnostic"])
        self.assertIsNone(state["fatal_error"])
        self.assertTrue(app.selectbox(key="selected_model").disabled)

    def test_footer_keeps_workflow_configuration_errors_fatal(self):
        with (
            patch(
                "src.ui.layout.footer.DockerLLM.list_models",
                return_value=(["ai/one"], None),
            ),
            patch(
                "src.ui.layout.footer.load_workflows",
                side_effect=WorkflowConfigurationError("workflow configuration is invalid"),
            ),
        ):
            app = AppTest.from_string(FOOTER_SCRIPT).run()

        self.assertFalse(app.exception)
        state = app.session_state["footer_test_state"]
        self.assertTrue(state["model_available"])
        self.assertEqual(state["fatal_error"], "workflow configuration is invalid")

    def test_app_renders_centered_warning_without_raw_docker_diagnostics(self):
        with (
            patch(
                "src.ui.layout.footer.DockerLLM.list_models",
                return_value=([], "docker command failed with private host details"),
            ),
            patch("src.ui.app.render_body") as render_body,
        ):
            app = AppTest.from_string(APP_SCRIPT).run()

        self.assertFalse(app.exception)
        app.get_by_key("model-unavailable")
        self.assertEqual(app.warning[0].value, MODEL_UNAVAILABLE_MESSAGE)
        self.assertNotIn(
            "private host details",
            " ".join(element.value for element in app.error),
        )
        self.assertTrue(app.selectbox(key="selected_model").disabled)
        render_body.assert_not_called()

    def test_unavailable_refresh_clears_partial_workflow_state(self):
        with (
            patch(
                "src.ui.layout.footer.DockerLLM.list_models",
                return_value=([], "docker unavailable"),
            ),
            patch("src.ui.app.render_body") as render_body,
            patch("src.Workflows.workflow.DockerLLM.call") as model_call,
        ):
            app = AppTest.from_string(APP_SCRIPT).run()
            app.session_state[ACTIVE_STEP_KEY] = 1
            app.session_state[MESSAGES_KEY] = {
                0: {"IsError": False, "Message": "partial query"},
            }
            app.session_state["workflow-query-9"] = "partial query"
            app.session_state["unrelated"] = "keep me"
            app = app.button(key="refresh").click().run()

        self.assertFalse(app.exception)
        self.assertEqual(app.warning[0].value, MODEL_UNAVAILABLE_MESSAGE)
        self.assertNotIn(ACTIVE_STEP_KEY, app.session_state)
        self.assertNotIn(MESSAGES_KEY, app.session_state)
        self.assertNotIn("workflow-query-9", app.session_state)
        self.assertEqual(app.session_state["unrelated"], "keep me")
        render_body.assert_not_called()
        model_call.assert_not_called()

    def test_app_renders_fatal_workflow_errors_without_the_model_warning(self):
        with (
            patch(
                "src.ui.layout.footer.DockerLLM.list_models",
                return_value=(["ai/one"], None),
            ),
            patch(
                "src.ui.layout.footer.load_workflows",
                side_effect=WorkflowConfigurationError("workflow configuration is invalid"),
            ),
        ):
            app = AppTest.from_string(APP_SCRIPT).run()

        self.assertFalse(app.exception)
        self.assertEqual(app.error[0].value, "workflow configuration is invalid")
        self.assertEqual(len(app.warning), 0)

    def test_real_entrypoint_starts_without_docker(self):
        with patch(
            "src.llm.docker_llm.subprocess.run",
            side_effect=FileNotFoundError("docker"),
        ):
            app = AppTest.from_file(PROJECT_ROOT / "main.py").run()

        self.assertFalse(app.exception)
        app.get_by_key("model-unavailable")
        self.assertEqual(app.warning[0].value, MODEL_UNAVAILABLE_MESSAGE)
        self.assertTrue(app.selectbox(key="selected_model").disabled)

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
