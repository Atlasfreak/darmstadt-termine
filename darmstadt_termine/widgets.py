from django.forms import TextInput


class DurationInput(TextInput):
    """
    DurationInput a custom widget to display a duration picker in a form.
    """

    class Media:
        js = [
            "darmstadt_termine/js/html-duration-picker.min.js",
        ]

    def __init__(self, attrs=None):
        if attrs is not None:
            attrs = attrs.copy()
            if "class" in attrs.keys():
                attrs["class"] += " html-duration-picker"
        else:
            attrs = {"class": "html-duration-picker"}
        super().__init__(attrs)
