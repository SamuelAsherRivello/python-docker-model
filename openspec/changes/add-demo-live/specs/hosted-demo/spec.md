# Spec Delta

## Purpose

Provide a publicly reachable Streamlit demonstration that remains understandable and stable when its hosted runtime cannot access local Docker Model Runner resources.

## ADDED Requirements

### Requirement: Public live demo
The project SHALL provide a public Streamlit demo URL that starts the application from the repository's `Python/` project and loads without requiring Docker to be installed in the hosted runtime.

#### Scenario: Visitor opens the live demo
- **WHEN** a visitor follows the repository's Live Demo link
- **THEN** the Streamlit application loads successfully at a public URL

#### Scenario: Hosted runtime has no Docker CLI
- **WHEN** the hosted runtime starts without the Docker CLI
- **THEN** the application remains available and renders its unavailable-model experience without an uncaught exception

### Requirement: Centered unavailable-model warning
The application SHALL render a prominent warning centered in the main content area when Docker Model Runner cannot be used or no runnable Docker models are available. The warning SHALL say “Docker Models not accessible. App designed to run locally, not yet online.”

#### Scenario: Docker command is unavailable
- **WHEN** model discovery reports that Docker cannot be executed
- **THEN** the centered unavailable-model warning is displayed instead of raw command diagnostics

#### Scenario: Docker model discovery fails
- **WHEN** model discovery exits unsuccessfully, times out, or returns invalid data
- **THEN** the centered unavailable-model warning is displayed and the page remains usable

#### Scenario: No runnable models are installed
- **WHEN** model discovery succeeds but returns no runnable model names
- **THEN** the centered unavailable-model warning is displayed

### Requirement: Model-dependent interaction is unavailable without models
The application MUST prevent model execution when no runnable Docker model is available, while keeping the page, its explanatory warning, and non-executing interface elements renderable.

#### Scenario: Visitor views the hosted fallback
- **WHEN** the unavailable-model warning is active
- **THEN** the model selector has no active choice and no workflow step can initiate a Docker model call

#### Scenario: Visitor refreshes the fallback
- **WHEN** a visitor refreshes while Docker Model Runner remains unavailable
- **THEN** the application returns to the same stable unavailable-model state without retaining a partial workflow run

### Requirement: Local Docker behavior is preserved
The application SHALL retain the existing model selection and workflow behavior when Docker Model Runner returns one or more runnable model names.

#### Scenario: Local models are accessible
- **WHEN** model discovery returns runnable model names
- **THEN** the warning is absent and the model and workflow controls operate normally

#### Scenario: Workflow omits the LLM step
- **WHEN** a locally usable workflow contains no `llm-prompt-step`
- **THEN** completing that workflow does not call Docker model inference

### Requirement: Demo documentation identifies the limitation
The repository documentation SHALL link to the deployed Streamlit URL and explain that hosted model inference is unavailable because Docker Model Runner is designed to run with the project locally.

#### Scenario: Reader reviews the Live Demo section
- **WHEN** a reader opens the repository README
- **THEN** the Live Demo section links to the public deployment and states the hosted inference limitation
