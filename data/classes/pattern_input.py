from kivy.uix.textinput import TextInput


class PatternInput(TextInput):

    def validate_text(self, text_input, text):
        # if the pattern is being breached, prevent it
        if text.find(self.immutable) == -1 or text.find(self.immutable) != len(text) - len(self.immutable):
            self.text = self.old_text
        else:
            self.old_text = text

    def get_pattern(self):
        return self.text.replace(self.immutable, "")

    def __init__(self, **kwargs):
        super(PatternInput, self).__init__(**kwargs)

        self.old_text = ""  # used to validate text that is typed in
        self.immutable = None   # unchangeable part of the text