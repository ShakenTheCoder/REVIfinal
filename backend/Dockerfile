FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download models at build time to avoid runtime delays
RUN python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
    model_name='cardiffnlp/twitter-xlm-roberta-base-sentiment'; \
    AutoTokenizer.from_pretrained(model_name); \
    AutoModelForSequenceClassification.from_pretrained(model_name)"

RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
