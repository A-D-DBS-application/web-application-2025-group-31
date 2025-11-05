def summarize_text(text):
    # Simple text summarization logic
    sentences = text.split('. ')
    if len(sentences) <= 2:
        return text  # Return the original text if it's too short to summarize
    summary = ' '.join(sentences[:2]) + '.'
    return summary

def summarize_data(data):
    # Assuming data is a list of text entries
    return [summarize_text(entry) for entry in data]