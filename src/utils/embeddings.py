from openai.embeddings_utils import get_embedding

class EmbeddingGenerator:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_embedding(self, text: str) -> list:
        embedding = get_embedding(text, model=self.model_name)
        return embedding

def main():
    # Example usage
    generator = EmbeddingGenerator(model_name="text-embedding-ada-002")
    sample_text = "This is a sample text for embedding."
    embedding = generator.generate_embedding(sample_text)
    print(embedding)

if __name__ == "__main__":
    main()