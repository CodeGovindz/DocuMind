# Use Python 3.10 slim image for AMD64 architecture
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PDF processing and ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies
# PyMuPDF for PDF processing and sentence-transformers for semantic analysis
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir PyMuPDF==1.23.22 sentence-transformers

# Copy application files
COPY 1B.py .
COPY pdf_extractor.py .

# Copy the local sentence transformer model for offline operation
COPY local_model/ ./local_model/

# Create directories and set permissions
RUN mkdir -p /app/input /app/output && \
    chmod 755 /app/input /app/output

# Run as non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set the entry point
CMD ["python", "1B.py"]