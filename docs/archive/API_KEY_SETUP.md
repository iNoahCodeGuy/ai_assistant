# Noah's AI Assistant - API Key Setup

## Setting up your OpenAI API Key

1. **Get your API key from OpenAI:**
   - Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new secret key
   - Copy the key (starts with `sk-`)

2. **Add your API key to the .env file:**
   - Open the `.env` file in the root directory
   - Replace `your_openai_api_key_here` with your actual API key
   
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Security Notes:**
   - The `.env` file is already in `.gitignore` so it won't be committed to Git
   - Never share your API key publicly
   - Never commit API keys to version control

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Test the setup:**
   ```bash
   python3 -c "from src.config.settings import Settings; s = Settings(); s.validate_api_key(); print('API key loaded successfully!')"
   ```

## Environment Variables

The following environment variables can be set in your `.env` file:

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `OPENAI_MODEL` - GPT model to use (default: gpt-3.5-turbo)
- `EMBEDDING_MODEL` - Embedding model (default: text-embedding-ada-002)
- `CAREER_KB_PATH` - Path to career knowledge base CSV
- `VECTOR_STORE_PATH` - Path to vector stores directory
- `ANALYTICS_DB` - Analytics database connection string

## Running the Application

After setting up your API key:

```bash
streamlit run src/main.py
```

The application will automatically load your API key from the `.env` file.
