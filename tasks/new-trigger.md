Feature: Interval Trigger Configuration
As a: Flow designer
I want to: Configure interval-based triggers
So that: I can automate flow execution at regular intervals

Acceptance Criteria:
- Can set interval duration in seconds
- Can set the message to be sent when the interval is triggered
- Can enable/disable interval trigger
- Receives validation feedback for invalid interval values
- Supports minimum interval of 1 second
- Shows visual indication of trigger status (active/inactive)

---

Feature: Event Trigger Management
As a: Flow designer
I want to: Configure event-based triggers
So that: I can execute flows based on specific events

Acceptance Criteria:
- Can define event types from other components
- Other components can be linked to the event trigger
- Can set conditions for event triggering
- Can set the message to be sent when the event is triggered
- Can enable/disable event trigger
- Receives validation feedback for invalid event values
- Supports minimum interval of 1 second
- Shows visual indication of trigger status (active/inactive)

NFR:
- Clear separation of trigger components
- Easy trigger debugging capabilities
- Modular trigger architecture
- Standardized error handling
- Clear logging and monitoring
