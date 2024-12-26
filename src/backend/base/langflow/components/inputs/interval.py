from langflow.base.io.interval import IntervalComponent
from langflow.io import Output, IntInput, StrInput
from langflow.schema.message import Message

class IntervalInputComponent(IntervalComponent):
    display_name = "Interval Input"
    description = "Get interval inputs from the Playground."
    icon = "clock"
    name = "IntervalInput"

    inputs = [
        IntInput(name="interval_time", display_name="Interval", info="The interval to be passed to the next component."),
        StrInput(name="interval_message", display_name="Trigger Message", info="The message to be passed to the next component."),
    ]
    outputs = [
        Output(display_name="Interval", name="interval_output", method="interval_response"),
    ]

    def interval_response(self) -> Message:
        return Message(
            text=self.interval_message,
        )
    
    def build_output(self):
        return Output(display_name="Interval", name="interval_output", method="interval_response")


    