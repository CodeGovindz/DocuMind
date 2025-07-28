# Persona-Driven Document Intelligence (Challenge 1B)

## Overview
This solution implements a persona-driven document analysis system that extracts and ranks relevant sections from multiple PDFs based on a specific persona and task. The system uses the `all-mpnet-base-v2` sentence transformer model for semantic similarity matching.

## Approach

### 1. Document Structure Extraction
- Utilizes the `PDFStructureExtractor` class from Challenge 1A to parse PDF documents
- Extracts hierarchical document structure including titles and headings (H1-H6)
- Processes text blocks while maintaining their spatial relationships

### 2. Semantic Analysis
- Employs the `all-mpnet-base-v2` sentence transformer model for:
  - Encoding document sections into dense vector representations
  - Calculating semantic similarity between the user's query (persona + task) and document sections
  - Ranking sections by relevance to the specified task

### 3. Key Components
- **Section Extraction**: Identifies and extracts meaningful document sections
- **Semantic Matching**: Uses transformer-based embeddings to find relevant content
- **Ranking System**: Ranks sections based on their relevance to the persona's task
- **Structured Output**: Generates well-formatted JSON output with ranked sections and metadata

## Dependencies

- Python 3.8+
- PyMuPDF (fitz)
- sentence-transformers
- torch
- numpy
- tqdm (for progress tracking)

## Installation

1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required packages:
   ```bash
   pip install pymupdf sentence-transformers torch numpy tqdm
   ```

3. Download the `all-mpnet-base-v2` model locally:
   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('all-mpnet-base-v2')
   model.save('local_model_path')
   ```

## Usage

### Basic Usage

```bash
python 1B.py --input_dir "path/to/pdf/directory" --config "path/to/config.json" --output_dir "output/directory"
```

### Input Format

Create a `challenge1b_input.json` file with the following structure:

```json
{
  "challenge_info": {
    "challenge_id": "round_1b_001",
    "persona": "Food Contractor",
    "job_to_be_done": "Prepare vegetarian buffet-style dinner menu for corporate gathering"
  }
}
```

### Output Format

The system generates a JSON file with the following structure:

```json
{
  "metadata": {
    "input_documents": ["document1.pdf"],
    "persona": "Food Contractor",
    "job_to_be_done": "Prepare vegetarian buffet-style dinner menu for corporate gathering",
    "processing_timestamp": "2025-07-28T16:45:30.123456"
  },
  "extracted_sections": [
    {
      "document": "document1.pdf",
      "page_number": 5,
      "section_title": "Vegetarian Main Courses",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "document1.pdf",
      "section_title": "Vegetarian Main Courses",
      "refined_text": "...extracted content...",
      "page_number": 5
    }
  ]
}
```

## Customization

### Model Configuration
- The system uses `all-mpnet-base-v2` by default
- To use a different model, modify the `model_path` in the script

### Performance Tuning
- Adjust the `max_section_length` parameter to control the size of extracted sections
- Modify the similarity threshold in the ranking function to be more or less selective

## Performance

- Processing time: ~2-5 seconds per document (varies by document size and system)
- Memory usage: ~1.5GB (primarily for the transformer model)
- Supports batch processing of multiple documents

## Testing

The solution includes three test collections:

1. **Travel Planning**: South of France travel guides
2. **Adobe Acrobat Learning**: Tutorials and guides
3. **Recipe Collection**: Cooking and meal planning

To test with a specific collection:

```bash
python 1B.py --input_dir "Collection 1/PDFs" --config "Collection 1/challenge1b_input.json" --output_dir "output"
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **CUDA Out of Memory**:
   - The script automatically falls back to CPU if GPU memory is insufficient
   - Reduce batch size or use a smaller model if needed

3. **PDF Parsing Errors**:
   - Ensure PDFs are not password protected
   - Verify that PDFs contain extractable text (not scanned images)

## License

This project is open source and available under the MIT License.
