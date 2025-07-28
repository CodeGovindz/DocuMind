# Use Python 3.10 slim image for AMD64 architecture
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PDF processing
# Keep it minimal for faster builds and smaller image size
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies
# PyMuPDF for PDF processing - pinned version for reproducibility
# sentence-transformers for text embeddings and semantic analysis
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir PyMuPDF==1.23.22 sentence-transformers

# Copy the main processing script
COPY 1A.py .

# Create input and output directories with proper permissions
RUN mkdir -p /app/input /app/output && \
    chmod 755 /app/input /app/output

# Run as non-root user for security (optional but good practice)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set the entry point to run the main processing script
CMD ["python", "1A.py"] 