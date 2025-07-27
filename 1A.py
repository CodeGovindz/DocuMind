
# import fitz  # PyMuPDF
# import json
# import os
# import re
# from collections import Counter
# from typing import List, Dict, Any

# class PDFStructureExtractor:
#     def __init__(self):
#         # Minimum font size difference to consider different heading levels (less relevant now)
#         self.font_size_threshold = 1.0

#         # Patterns used to identify titles
#         self.title_patterns = [
#             r'^[A-Z][A-Za-z\s:]{10,100}$',  # Title-like capitalization
#             r'^[A-Z\s]{10,100}$',            # All caps lines
#         ]

#         # Patterns to detect headings
#         self.heading_patterns = [
#             r'^\d+\.\d+\.\d+\s+.+',  # H3 like: 1.1.1
#             r'^\d+\.\d+\s+.+',        # H2 like: 1.1
#             r'^\d+\s+.+',               # H1 like: 1
#             r'^[A-Z][A-Za-z\s]{3,50}$',  # Capitalized
#             r'^[A-Z][^a-z]+$',            # All caps headings
#         ]

#     def extract_text_with_formatting(self, pdf_path: str) -> List[Dict[str, Any]]:
#         """Extract text with font information from PDF."""
#         doc = fitz.open(pdf_path)
#         text_blocks = []

#         for page_num in range(len(doc)):
#             page = doc[page_num]
#             blocks = page.get_text("dict")

#             for block in blocks.get("blocks", []):
#                 for line in block.get("lines", []):
#                     for span in line.get("spans", []):
#                         text = span["text"].strip()
#                         if text:
#                             text_blocks.append({
#                                 "text": text,
#                                 "font": span["font"],
#                                 "size": span["size"],
#                                 "flags": span["flags"],
#                                 "page": page_num + 1,
#                                 "bbox": span["bbox"]
#                             })
#         doc.close()
#         return text_blocks

#     def analyze_font_sizes(self, text_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """Determine the most common font size (assumed body text size)."""
#         sizes = [block["size"] for block in text_blocks]
#         size_counter = Counter(sizes)
#         body_size = size_counter.most_common(1)[0][0] if sizes else 12
#         return {"body_size": body_size}

#     def is_likely_title(self, text: str, font_info: Dict[str, Any]) -> bool:
#         """Heuristically determine if text is a document title."""
#         if not (5 <= len(text) <= 200):
#             return False
#         for pattern in self.title_patterns:
#             if re.match(pattern, text):
#                 return True
#         # Large font
#         return font_info.get("size", 0) > font_info.get("body_size", 12) + 4

#     def is_likely_heading(self, text: str) -> bool:
#         """Determine if text matches heading patterns."""
#         for pattern in self.heading_patterns:
#             if re.match(pattern, text):
#                 return True
#         return False

#     def get_heading_level(self, text: str) -> str:
#         """Guess heading level from numbering pattern."""
#         if re.match(r'^\d+\.\d+\.\d+', text):
#             return "H3"
#         elif re.match(r'^\d+\.\d+', text):
#             return "H2"
#         elif re.match(r'^\d+', text):
#             return "H1"
#         else:
#             return "H1"

#     def extract_document_structure(self, pdf_path: str) -> Dict[str, Any]:
#         """Extract document title and structured outline."""
#         text_blocks = self.extract_text_with_formatting(pdf_path)
#         if not text_blocks:
#             return {"title": "", "outline": []}

#         font_info = self.analyze_font_sizes(text_blocks)
#         body_size = font_info["body_size"]

#         title = ""
#         outline = []

#         for block in text_blocks[:20]:
#             if self.is_likely_title(block["text"], {**font_info, **block}):
#                 title = block["text"]
#                 break

#         if not title:
#             first_page_blocks = [b for b in text_blocks if b["page"] == 1]
#             if first_page_blocks:
#                 largest_block = max(first_page_blocks, key=lambda x: x["size"])
#                 if largest_block["size"] > body_size + 2:
#                     title = largest_block["text"]

#         for block in text_blocks:
#             text = block["text"]
#             if text == title:
#                 continue
#             if self.is_likely_heading(text):
#                 outline.append({
#                     "level": self.get_heading_level(text),
#                     "text": text,
#                     "page": block["page"]
#                 })

#         return {"title": title, "outline": outline}

# def process_pdfs(input_dir: str, output_dir: str):
#     """Process all PDFs in input directory and save JSON outputs."""
#     os.makedirs(output_dir, exist_ok=True)
#     extractor = PDFStructureExtractor()

#     for filename in os.listdir(input_dir):
#         if filename.lower().endswith('.pdf'):
#             pdf_path = os.path.join(input_dir, filename)
#             output_filename = filename.replace('.pdf', '.json')
#             output_path = os.path.join(output_dir, output_filename)

#             try:
#                 structure = extractor.extract_document_structure(pdf_path)
#                 with open(output_path, 'w', encoding='utf-8') as f:
#                     json.dump(structure, f, indent=2, ensure_ascii=False)
#                 print(f"Processed: {filename} -> {output_filename}")
#             except Exception as e:
#                 print(f"Error processing {filename}: {str(e)}")

# if __name__ == "__main__":
#     base_dir = "C:/Users/bhart/Downloads/Coding/Python/contest/app"
#     input_directory = os.path.join(base_dir, "input")
#     output_directory = os.path.join(base_dir, "output")

#     os.makedirs(input_directory, exist_ok=True)
#     os.makedirs(output_directory, exist_ok=True)

#     process_pdfs(input_directory, output_directory)

# Improved PDF Structure Extraction Based on Font Size and Layout

# import fitz  # PyMuPDF
# import json
# import os
# import re
# from collections import defaultdict
# from typing import List, Dict, Any,Tuple

# class PDFStructureExtractor:
#     def __init__(self):
#         self.fallback_labels = ["TITLE", "H1", "H2", "H3"]

#     def extract_text_by_font(self, pdf_path: str) -> Tuple[List[Dict[float, List[Tuple[float, str]]]], List[float]]:
#         """Extract paragraphs grouped by font size and ordered by vertical position."""
#         doc = fitz.open(pdf_path)
#         page_font_maps = []
#         all_sizes = set()

#         for page in doc:
#             para_map = defaultdict(list)
#             blocks = page.get_text("dict").get("blocks", [])
#             for block in blocks:
#                 for line in block.get("lines", []):
#                     for span in line.get("spans", []):
#                         text = span["text"].strip()
#                         if not text:
#                             continue
#                         size = round(span["size"], 1)
#                         y_pos = span["bbox"][1]
#                         para_map[size].append((y_pos, text))
#                         all_sizes.add(size)
#             # Sort each font size's entries by vertical position
#             for size in para_map:
#                 para_map[size].sort(key=lambda x: x[0])
#             page_font_maps.append(para_map)
#         doc.close()
#         return page_font_maps, sorted(all_sizes, reverse=True)

#     def assign_heading_levels(self, sorted_sizes: List[float]) -> Dict[float, str]:
#         """Assign font sizes to heading levels based on order."""
#         if len(sorted_sizes) == 1:
#             return {sorted_sizes[0]: "BODY"}  # fallback case

#         size_map = {}
#         for i, size in enumerate(sorted_sizes):
#             label = self.fallback_labels[i] if i < len(self.fallback_labels) else "BODY"
#             size_map[size] = label
#         return size_map

#     def extract_document_structure(self, pdf_path: str) -> Dict[str, Any]:
#         """Extract structured title and heading outline using layout and font sizes."""
#         page_font_maps, sorted_sizes = self.extract_text_by_font(pdf_path)
#         size_to_label = self.assign_heading_levels(sorted_sizes)

#         title = ""
#         outline = []

#         for page_num, para_map in enumerate(page_font_maps):
#             for size in para_map:
#                 label = size_to_label.get(size, "BODY")
#                 for _, text in para_map[size]:
#                     if not title and label == "TITLE" and len(text.split()) > 2:
#                         title = text
#                     elif label in ["H1", "H2", "H3"]:
#                         outline.append({
#                             "level": label,
#                             "text": text,
#                             "page": page_num + 1
#                         })

#         # Fallback for title if not found
#         if not title and outline:
#             title = outline[0]["text"]

#         return {"title": title, "outline": outline}

# def process_pdfs(input_dir: str, output_dir: str):
#     """Process all PDFs in input directory and save JSON outputs."""
#     os.makedirs(output_dir, exist_ok=True)
#     extractor = PDFStructureExtractor()

#     for filename in os.listdir(input_dir):
#         if filename.lower().endswith('.pdf'):
#             pdf_path = os.path.join(input_dir, filename)
#             output_filename = filename.replace('.pdf', '.json')
#             output_path = os.path.join(output_dir, output_filename)

#             try:
#                 structure = extractor.extract_document_structure(pdf_path)
#                 with open(output_path, 'w', encoding='utf-8') as f:
#                     json.dump(structure, f, indent=2, ensure_ascii=False)
#                 print(f"Processed: {filename} -> {output_filename}")
#             except Exception as e:
#                 print(f"Error processing {filename}: {str(e)}")

# if __name__ == "__main__":
#     base_dir = "C:/Users/bhart/Downloads/Coding/Python/contest/app"
#     input_directory = os.path.join(base_dir, "input")
#     output_directory = os.path.join(base_dir, "output")

#     os.makedirs(input_directory, exist_ok=True)
#     os.makedirs(output_directory, exist_ok=True)

#     process_pdfs(input_directory, output_directory)

import fitz  # PyMuPDF
import json
import os
import re
from collections import defaultdict
from typing import List, Dict, Any, Tuple

class PDFStructureExtractor:
    def __init__(self):
        self.heading_labels = ["H1", "H2", "H3", "H4", "H5", "H6"]
    
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
    
    def _has_normal_character_spacing(self, text: str) -> bool:
        """
        Check if text has normal character spacing.
        Reject text with excessive spaces like 'abc     50'.
        """
        # Remove leading/trailing spaces
        text = text.strip()
        if not text:
            return False
        
        # Check for excessive spacing (more than 2 consecutive spaces)
        if re.search(r'  +', text):  # 2 or more consecutive spaces
            return False
        
        # Additional check: if text has numbers separated by many spaces, likely not a heading
        if re.search(r'\w\s{2,}\d', text) or re.search(r'\d\s{2,}\w', text):
            return False
            
        return True
    
    def _is_line_positioned_correctly(self, line_bbox: Tuple[float, float, float, float], 
                                     page_width: float) -> bool:
        """
        Check if line is positioned at extreme left or middle of the page.
        """
        x0, y0, x1, y1 = line_bbox
        line_width = x1 - x0
        
        # Define thresholds
        left_margin_threshold = page_width * 0.15  # Within 15% from left edge
        center_start = page_width * 0.3  # Center area starts at 30%
        center_end = page_width * 0.7    # Center area ends at 70%
        
        # Check if line starts at extreme left
        is_extreme_left = x0 <= left_margin_threshold
        
        # Check if line is centered (starts somewhere in the center region)
        line_center = x0 + (line_width / 2)
        is_centered = center_start <= line_center <= center_end
        
        return is_extreme_left or is_centered
    
    def _is_line_fully_bold(self, line_spans: List[Dict[str, Any]]) -> bool:
        """Check if all spans in a line are bold."""
        if not line_spans:
            return False
        return all(self._is_span_bold(span) for span in line_spans)
    
    def extract_headings_by_page(self, pdf_path: str) -> Tuple[List[Dict[float, List[str]]], List[float], str]:
        """
        Extract bold headings from each page, grouped by font size.
        Returns: (page_headings, all_font_sizes, document_title)
        """
        doc = fitz.open(pdf_path)
        
        # Get document title from metadata
        metadata = doc.metadata
        document_title = metadata.get('title', '') or metadata.get('subject', '') or "Untitled Document"
        
        page_headings = []
        all_font_sizes = set()
        
        for page_num, page in enumerate(doc):
            page_width = page.rect.width
            headings_by_size = defaultdict(list)
            
            # Get text with detailed information
            blocks = page.get_text("dict").get("blocks", [])
            
            for block in blocks:
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue
                    
                    # Reconstruct line text
                    line_text = "".join(span["text"] for span in spans)
                    line_text = line_text.strip()
                    
                    if not line_text:
                        continue
                    
                    # Check if line meets all criteria
                    line_bbox = line.get("bbox", (0, 0, 0, 0))
                    is_bold = self._is_line_fully_bold(spans)
                    has_normal_spacing = self._has_normal_character_spacing(line_text)
                    is_positioned_correctly = self._is_line_positioned_correctly(line_bbox, page_width)
                    
                    # Only include lines that meet all criteria
                    if is_bold and has_normal_spacing and is_positioned_correctly:
                        # Use the font size of the first span as representative
                        font_size = round(spans[0]["size"], 1)
                        headings_by_size[font_size].append(line_text)
                        all_font_sizes.add(font_size)
            
            page_headings.append(dict(headings_by_size))
        
        doc.close()
        return page_headings, sorted(list(all_font_sizes), reverse=True), document_title
    
    def create_font_hierarchy(self, sorted_font_sizes: List[float]) -> Dict[float, str]:
        """Create hierarchy mapping from font sizes to heading levels."""
        font_to_level = {}
        
        for i, font_size in enumerate(sorted_font_sizes):
            if i < len(self.heading_labels):
                font_to_level[font_size] = self.heading_labels[i]
            else:
                # For more than 6 levels, use H6+ format
                font_to_level[font_size] = f"H{6 + (i - 5)}"
        
        return font_to_level
    
    def extract_document_structure(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract complete document structure with page-by-page headings.
        """
        page_headings, sorted_font_sizes, document_title = self.extract_headings_by_page(pdf_path)
        font_hierarchy = self.create_font_hierarchy(sorted_font_sizes)
        
        # Build structured output
        structure = {
            "title": document_title,
            "font_hierarchy": {
                size: level for size, level in font_hierarchy.items()
            },
            "pages": []
        }
        
        # Process each page
        for page_num, page_heading_dict in enumerate(page_headings):
            page_structure = {
                "page_number": page_num + 1,
                "headings": []
            }
            
            # Process headings in font size order (largest to smallest)
            for font_size in sorted_font_sizes:
                if font_size in page_heading_dict:
                    heading_level = font_hierarchy[font_size]
                    for heading_text in page_heading_dict[font_size]:
                        page_structure["headings"].append({
                            "level": heading_level,
                            "font_size": font_size,
                            "text": heading_text
                        })
            
            structure["pages"].append(page_structure)
        
        return structure

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
            print(f"  ✓ Found {len(structure['pages'])} pages")
            
            # Print summary of headings found
            total_headings = sum(len(page['headings']) for page in structure['pages'])
            print(f"  ✓ Total headings found: {total_headings}")
            
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
