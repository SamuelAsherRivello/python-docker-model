## ADDED Requirements

### Requirement: Step cards use a consistent ordered header

The application SHALL render every workflow step in a StepCard whose horizontal header shows the step's one-based workflow position and display name on the left and its lifecycle status on the right.

#### Scenario: Cards show workflow order

- **WHEN** a workflow with three steps is rendered
- **THEN** the card headers identify the steps as `Step 1`, `Step 2`, and `Step 3` in configuration order
- **AND** each number is shown with that step's display name

#### Scenario: Status is visible as text

- **WHEN** any StepCard is rendered
- **THEN** its header shows exactly one textual status from `Unstarted`, `Active`, or `Complete`
- **AND** the status remains understandable without relying on color

### Requirement: Card statuses reflect workflow lifecycle

The application SHALL derive each card's status from the current workflow run and SHALL render no more than one `Active` card at a time.

#### Scenario: Initial workflow state

- **WHEN** a new workflow run is ready for user input
- **THEN** the Query card is `Active`
- **AND** every later card is `Unstarted`

#### Scenario: Successful step advances activity

- **WHEN** the active step finishes processing
- **THEN** that card becomes `Complete`
- **AND** the next card becomes `Active`
- **AND** no other card is `Active`

#### Scenario: Completed workflow has no active card

- **WHEN** the final step has finished processing
- **THEN** every card is `Complete`
- **AND** zero cards are `Active`

#### Scenario: Error processing still completes lifecycle

- **WHEN** a step returns a message with `IsError=True`
- **THEN** that step becomes `Complete` after processing
- **AND** the error continues through subsequent workflow steps under the existing propagation rules

### Requirement: Step cards use a shared body layout

The application SHALL render each card body in label, value, and action regions in that order, using consistent alignment across step types.

#### Scenario: Query card layout

- **WHEN** a Query card is rendered
- **THEN** its label is `Input Text`
- **AND** its value region contains the query text area
- **AND** its action region contains the Submit button
- **AND** the label, text area, and Submit button are rendered on one horizontal line

#### Scenario: LLM card layout

- **WHEN** an LLM prompt card is rendered
- **THEN** its label is `Response`
- **AND** its value region displays the generated model response when available
- **AND** its action region is reserved but contains no control

#### Scenario: Output card layout

- **WHEN** an Output card is rendered
- **THEN** its label is `Output`
- **AND** its value region displays the final workflow message when available
- **AND** its action region is reserved but contains no control

#### Scenario: Error output remains distinct

- **WHEN** the Output card receives a message with `IsError=True`
- **THEN** its value region renders the error message in red text

### Requirement: Only the active card is interactive

The application SHALL keep all configured cards visible while disabling and visually muting every card that is not `Active`.

#### Scenario: Future step is disabled

- **WHEN** a card is `Unstarted`
- **THEN** the card remains visible and greyed out
- **AND** the user cannot interact with controls in that card

#### Scenario: Completed step is disabled

- **WHEN** a card is `Complete`
- **THEN** its recorded value remains visible
- **AND** the user cannot interact with controls in that card

#### Scenario: Submitted query remains in its completed card

- **WHEN** the user submits `hello` from the active Query card
- **AND** the Query card becomes `Complete`
- **THEN** its text area still displays `hello`
- **AND** its text area and Submit button are disabled
- **AND** only the card status and enabled state change

### Requirement: Query entry supports keyboard submission and multiline input

The active Query card SHALL support submission by keyboard and button without sacrificing multiline input.

#### Scenario: Enter submits

- **WHEN** focus is in the active query text area
- **AND** the user presses Enter without Shift
- **THEN** the current query is submitted exactly once
- **AND** successful processing activates the next step

#### Scenario: Shift Enter adds a newline

- **WHEN** focus is in the active query text area
- **AND** the user presses Shift+Enter
- **THEN** a newline is inserted at the cursor
- **AND** the query is not submitted

#### Scenario: Submit button remains available

- **WHEN** the user activates the Submit button on the active Query card
- **THEN** the current query follows the same submission path as keyboard submission
