from langflow.custom import Component

class IntervalComponent(Component):
    display_name = "Interval Component"
    description = "Used to pass interval to the next component."
    icon = "clock"
    name = "Interval"

    def build_config(self):
        return {
            "interval": {
                "display_name": "Interval",
                "info": "The interval to be passed to the next component.",
            },
        }

