import fitz  # PyMuPDF
import json
import os
import re
from collections import defaultdict
from typing import List, Dict, Any, Tuple

class PDFStructureExtractor:
    def __init__(self):
        self.heading_labels = ["H1", "H2", "H3", "H4", "H5", "H6"]
        # Common header/footer patterns to exclude
        self.exclude_patterns = [
            r'^RFP:\s*To Develop.*Business Plan.*$',
            r'^March\s+\d{4}$',
            r'^\d+$',  # Just page numbers
            r'^Page\s+\d+.*$',
            r'^\s*$'  # Empty strings
        ]
    
    def _should_exclude_text(self, text: str) -> bool:
        """Check if text should be excluded (headers, footers, page numbers)."""
        text = text.strip()
        if not text:
            return True
            
        for pattern in self.exclude_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_span_bold(self, span: Dict[str, Any]) -> bool:
        """Check if a text span is bold based on font name or flags."""
        font_name = span.get('font', '').lower()
        flags = span.get('flags', 0)
        
        # Check font name for bold indicators
        bold_indicators = ['bold', 'black', 'heavy', 'semibold']
        font_is_bold = any(indicator in font_name for indicator in bold_indicators)
        
        # Check font flags (bit 4 is typically bold in PDF)
        flag_is_bold = bool(flags & 2**4)
        
        return font_is_bold or flag_is_bold
    
    def extract_text_blocks_by_position(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text blocks grouped by vertical position to handle fragmentation."""
        doc = fitz.open(pdf_path)
        all_elements = []
        
        for page_num, page in enumerate(doc):
            # Get all text elements with their positions
            text_dict = page.get_text("dict")
            elements_by_line = defaultdict(list)
            
            # Group spans by approximate Y position (line)
            for block in text_dict.get("blocks", []):
                if "lines" not in block:
                    continue
                
                for line in block["lines"]:
                    line_y = round(line["bbox"][1], 1)  # Round Y position
                    
                    for span in line["spans"]:
                        if span["text"].strip():
                            elements_by_line[line_y].append({
                                "text": span["text"],
                                "font_size": span["size"],
                                "is_bold": self._is_span_bold(span),
                                "x": span["bbox"][0],
                                "font": span["font"],
                                "flags": span["flags"]
                            })
            
            # Reconstruct lines by combining spans with similar Y positions
            for y_pos in sorted(elements_by_line.keys()):
                spans = elements_by_line[y_pos]
                if not spans:
                    continue
                
                # Sort by X position to get correct reading order
                spans.sort(key=lambda s: s["x"])
                
                # Combine text from spans
                combined_text = "".join(span["text"] for span in spans).strip()
                
                if not combined_text or self._should_exclude_text(combined_text):
                    continue
                
                # Determine if line is bold (majority of spans are bold)
                bold_count = sum(1 for span in spans if span["is_bold"])
                is_bold = bold_count > len(spans) / 2
                
                # Get representative font size (max font size in the line)
                font_size = max(span["font_size"] for span in spans)
                
                # Only keep meaningful headings
                if (is_bold and 
                    len(combined_text) > 3 and 
                    len(combined_text) < 200 and
                    not re.match(r'^[^a-zA-Z]*$', combined_text)):  # Has letters
                    
                    all_elements.append({
                        "text": combined_text,
                        "page": page_num + 1,
                        "font_size": round(font_size, 1),
                        "is_bold": is_bold,
                        "y_pos": y_pos
                    })
        
        doc.close()
        return all_elements
    
    def extract_title(self, pdf_path: str) -> str:
        """Extract document title."""
        doc = fitz.open(pdf_path)
        
        # Try metadata first
        metadata = doc.metadata
        title = metadata.get('title', '') or metadata.get('subject', '')
        
        if not title:
            # Look for title-like text on first page
            first_page = doc[0]
            
            # Use simple text extraction to find potential titles
            text_blocks = first_page.get_text("blocks")
            title_candidates = []
            
            for block in text_blocks:
                text = block[4].strip()  # Text content
                if (len(text) > 10 and 
                    any(word in text.lower() for word in ['rfp', 'request', 'proposal', 'ontario', 'digital', 'library'])):
                    title_candidates.append(text)
            
            if title_candidates:
                # Take the longest meaningful title
                title = max(title_candidates, key=len)
        
        doc.close()
        return title or "Untitled Document"
    
    def create_font_hierarchy(self, sorted_font_sizes: List[float]) -> Dict[float, str]:
        """Create hierarchy mapping from font sizes to heading levels."""
        font_to_level = {}
        
        for i, font_size in enumerate(sorted_font_sizes):
            if i < len(self.heading_labels):
                font_to_level[font_size] = self.heading_labels[i]
            else:
                font_to_level[font_size] = f"H{6 + (i - 5)}"
        
        return font_to_level
    
    def clean_and_filter_headings(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and filter headings to remove duplicates and fragments."""
        cleaned = []
        seen_texts = set()
        
        # Sort by page and position
        elements.sort(key=lambda x: (x["page"], x["y_pos"]))
        
        for element in elements:
            text = element["text"].strip()
            
            # Skip very short fragments
            if len(text) < 4:
                continue
            
            # Skip if we've seen similar text
            if any(text in seen or seen in text for seen in seen_texts):
                continue
            
            # Skip obvious fragments (text that doesn't start with capital or number)
            if not re.match(r'^[A-Z0-9]', text):
                continue
            
            # Skip if text is mostly punctuation
            if len(re.sub(r'[^a-zA-Z0-9\s]', '', text)) < len(text) * 0.5:
                continue
            
            seen_texts.add(text)
            cleaned.append(element)
        
        return cleaned
    
    def extract_document_structure(self, pdf_path: str) -> Dict[str, Any]:
        """Extract complete document structure in the expected format."""
        # Extract title
        title = self.extract_title(pdf_path)
        
        # Extract all text elements
        elements = self.extract_text_blocks_by_position(pdf_path)
        
        # Clean and filter headings
        headings = self.clean_and_filter_headings(elements)
        
        # Get unique font sizes and create hierarchy
        if headings:
            font_sizes = sorted(list(set(h["font_size"] for h in headings)), reverse=True)
            font_hierarchy = self.create_font_hierarchy(font_sizes)
            
            # Build outline
            outline = []
            for heading in headings:
                # Skip if this text is part of the title
                if heading["text"] in title or title in heading["text"]:
                    continue
                
                font_size = heading["font_size"]
                level = font_hierarchy.get(font_size, "H6")
                
                outline.append({
                    "level": level,
                    "text": heading["text"],
                    "page": heading["page"]
                })
        else:
            outline = []
        
        return {
            "title": title,
            "outline": outline
        }

def process_pdfs(input_dir: str, output_dir: str):
    """Process all PDFs in input directory and save structured JSON outputs."""
    os.makedirs(output_dir, exist_ok=True)
    extractor = PDFStructureExtractor()
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in the input directory.")
        return
    
    for filename in pdf_files:
        pdf_path = os.path.join(input_dir, filename)
        base_filename = os.path.splitext(filename)[0]
        output_filename = f"{base_filename}.json"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"Processing: {filename}...")
        try:
            structure = extractor.extract_document_structure(pdf_path)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(structure, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Saved structure to {output_filename}")
            print(f"  ✓ Title: {structure['title']}")
            print(f"  ✓ Found {len(structure['outline'])} headings")
            
            # Print summary of headings found by level
            heading_levels = {}
            for heading in structure['outline']:
                level = heading['level']
                heading_levels[level] = heading_levels.get(level, 0) + 1
            
            if heading_levels:
                level_summary = ", ".join([f"{level}: {count}" for level, count in sorted(heading_levels.items())])
                print(f"  ✓ Heading breakdown: {level_summary}")
                
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")

if __name__ == "__main__":
    # Configuration - Update these paths to match your setup
    base_dir = "contest/app"
    input_directory = os.path.join(base_dir, "input")
    output_directory = os.path.join(base_dir, "output")
    
    # Create directories if they don't exist
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    
    print("PDF Structure Extractor")
    print("=" * 50)
    print(f"Input directory: {input_directory}")
    print(f"Output directory: {output_directory}")
    print()
    
    # Check for PDF files
    try:
        pdf_count = len([f for f in os.listdir(input_directory) if f.lower().endswith('.pdf')])
        print(f"Found {pdf_count} PDF file(s) to process.")
        print()
        
        if pdf_count == 0:
            print("Please add PDF files to the input directory and run again.")
        else:
            process_pdfs(input_directory, output_directory)
            
    except FileNotFoundError:
        print(f"Error: Input directory '{input_directory}' not found.")
        print("Please create the directory and add PDF files to it.")
    
    print("\nProcessing complete!")
