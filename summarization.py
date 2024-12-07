from transformers import BartTokenizer, BartForConditionalGeneration

class BartSummarizer:
    def __init__(self):
        # Load pre-trained BART model and tokenizer
        self.tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
        self.model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

    def summarize(self, text, max_length=60, min_length=20, length_penalty=2.0, num_beams=4):
        """Generates a summary for a given text."""
        # Tokenize the input text
        inputs = self.tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)

        # Generate summary using BART
        summary_ids = self.model.generate(
            inputs['input_ids'],
            max_length=max_length,
            min_length=min_length,
            length_penalty=length_penalty,
            num_beams=num_beams,
            early_stopping=True
        )

        # Decode the summary
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return summary