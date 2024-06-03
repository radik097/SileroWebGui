import xml.etree.ElementTree as ET

class TextToSSMLConverter:
    def __init__(self):
        pass

    def process_long_text(self, text):
        """
        Process a long text by splitting it into smaller parts and wrapping with SSML tags.
        """
        ssml_parts = self.split_text(text)
        ssml_parts = [self.wrap_with_ssml(part) for part in ssml_parts]
        return ssml_parts

    def split_text(self, text, max_length=1000):
        """
        Split the text into smaller parts, each with a maximum length.
        """
        words = text.split()
        current_length = 0
        current_part = []
        parts = []

        for word in words:
            if current_length + len(word) + 1 > max_length:
                parts.append(" ".join(current_part))
                current_part = []
                current_length = 0
            current_part.append(word)
            current_length += len(word) + 1

        if current_part:
            parts.append(" ".join(current_part))

        return parts

    def wrap_with_ssml(self, text):
        """
        Wrap the given text with SSML tags.
        """
        ssml = f"<speak>{text}</speak>"
        return ssml
