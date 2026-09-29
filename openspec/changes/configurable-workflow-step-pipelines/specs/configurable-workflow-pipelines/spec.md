# Spec Delta

## Purpose

Provides configurable, sequential workflow experiences in the Streamlit application while keeping each step connected through a consistent message contract and preserving existing Docker model behavior.

## ADDED Requirements

### Requirement: Workflow configuration
The system SHALL load named workflows from a JSON configuration containing ordered step type names.

#### Scenario: Default workflows are available
- **WHEN** the application loads the workflow configuration
- **THEN** the workflow selector includes `Workflow 1` with query and output steps and `Workflow 2` with query, LLM prompt, and output steps

#### Scenario: Workflow selection changes
- **WHEN** a user selects a different configured workflow
- **THEN** the application resets the current run and renders the selected workflow's ordered steps

### Requirement: Workflow step rendering
The system SHALL render one visible step card for every step in the selected workflow, with only the active step enabled for interaction and inactive steps visibly disabled or greyed out.

#### Scenario: Initial workflow state
- **WHEN** a workflow is selected or reset
- **THEN** the first step is active and all later steps are visible but inactive

#### Scenario: Successful step progression
- **WHEN** the active step successfully processes its input
- **THEN** the system stores its output and activates the next step automatically

### Requirement: Shared step messages
Every workflow step SHALL accept and return a message containing `IsError` and `Message`, where `Message` contains either successful content or an error description.

#### Scenario: Successful message processing
- **WHEN** a step receives a non-error message and completes successfully
- **THEN** it returns `IsError` set to false and the step result in `Message`

#### Scenario: Error propagation
- **WHEN** a step returns `IsError` set to true
- **THEN** subsequent steps receive the error message unchanged and preserve the error state

### Requirement: Query and model processing
The system SHALL provide a query step that collects the user's query and an LLM prompt step that sends the incoming message to the selected Docker model.

#### Scenario: Query-only workflow
- **WHEN** the selected workflow contains query and output steps only
- **THEN** the query is passed directly to the output step and no Docker model call occurs

#### Scenario: LLM workflow
- **WHEN** the selected workflow contains an LLM prompt step and the query step succeeds
- **THEN** the incoming query is sent to the selected Docker model and the model response is passed to the next step

#### Scenario: Model failure
- **WHEN** the Docker model call fails
- **THEN** the LLM step returns an error message with `IsError` set to true and the workflow continues to the output step

### Requirement: Output and reset behavior
The output step SHALL render the incoming message, using red text for errors, and the system SHALL reset workflow state when the selected model, selected workflow, or application session is reset.

#### Scenario: Successful output
- **WHEN** the output step receives a successful message
- **THEN** it renders the message as normal output

#### Scenario: Error output
- **WHEN** the output step receives an error message
- **THEN** it renders the error message in red text

#### Scenario: Model or workflow changes
- **WHEN** the user changes the model or workflow
- **THEN** the active step and stored step messages are cleared and the newly selected workflow starts at its first step
