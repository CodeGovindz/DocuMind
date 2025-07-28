# PDF Structure Extractor

A Python script that extracts structured outlines (titles and headings) from PDF documents.

## Approach

The solution uses a rule-based approach to analyze PDF documents and extract their hierarchical structure. It focuses on:

1. **Title Extraction**:
   - First checks PDF metadata for title/subject
   - Falls back to analyzing text on the first page
   - Looks for title-like text based on position and content patterns

2. **Heading Detection**:
   - Identifies potential headings based on font weight (bold) and size
   - Groups text by vertical position to handle multi-line headings
   - Creates a hierarchy based on font sizes (larger fonts → higher heading levels)
   - Filters out common noise (page numbers, headers, footers)

3. **Output Generation**:
   - Produces a clean JSON structure with title and outline
   - Each outline item includes the heading level, text, and page number

## Dependencies

- Python 3.10+
- PyMuPDF (`fitz`)
- Standard libraries: `json`, `os`, `re`, `typing`, `collections`

## Installation

1. Install the required package:
   ```bash
   pip install pymupdf
   ```

## Usage

### Basic Usage

```bash
python 1A.py <input_pdf_path> <output_json_path>
```

### Example

```bash
# Process a single PDF
python 1A.py sample.pdf output.json

# Process all PDFs in a directory
mkdir -p output
for pdf in input/*.pdf; do
    python 1A.py "$pdf" "output/$(basename "$pdf" .pdf).json"
done
```

### Input

- PDF file path (positional argument 1)
- Output JSON file path (positional argument 2, optional - defaults to `output.json`)

### Output

A JSON file with the following structure:

```json
{
  "title": "Document Title",
  "outline": [
    {"level": "H1", "text": "Main Heading", "page": 1},
    {"level": "H2", "text": "Subheading", "page": 2},
    {"level": "H3", "text": "Nested Subheading", "page": 2}
  ]
}
```

## Customization

You can modify the following parameters in the script:

- `self.heading_labels`: Change the heading hierarchy
- `self.exclude_patterns`: Add patterns to filter out specific text
- `_is_span_bold()`: Adjust bold detection logic
- `_should_exclude_text()`: Modify text filtering rules

## Testing

A sample dataset is provided in the `sample_dataset` directory:

```
sample_dataset/
├── outputs/         # Expected JSON outputs
├── pdfs/            # Input PDF files
└── schema/          # Output schema definition
```

To test with the sample data:

```bash
# Create output directory
mkdir -p output

# Process all sample PDFs
for pdf in sample_dataset/pdfs/*.pdf; do
    python 1A.py "$pdf" "output/$(basename "$pdf" .pdf).json"
done
```

## Performance

- Processing time: Typically under 10 seconds for a 50-page PDF
- Memory usage: Optimized to work within standard system constraints
- CPU: Single-threaded operation

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```bash
   pip install pymupdf
   ```

2. **Font Detection**:
   - Check if the PDF contains text (not scanned images)
   - Verify that the text has proper font styling

3. **Incorrect Headings**:
   - Adjust the font size thresholds in the script
   - Modify the heading detection logic in `extract_text_blocks_by_position()`

## License

This project is open source and available under the MIT License.
