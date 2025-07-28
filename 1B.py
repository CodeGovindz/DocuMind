# import os
# import json
# import re
# from datetime import datetime
# from sentence_transformers import SentenceTransformer, util as st_util

# from pdf_extractor import PDFStructureExtractor  # Leverage your provided code!
# import fitz # PyMuPDF

# def extract_section_chunks(pdf_path, headings, max_section_length=4000):
#     doc = fitz.open(pdf_path)
#     results = []
#     # Find heading locations
#     heading_indices = []
#     for heading in headings:
#         page_num = heading['page'] - 1  # fitz uses 0-based
#         heading_text = heading['text']
#         found = False
#         page = doc[page_num]
#         for block in page.get_text("dict")["blocks"]:
#             if "lines" not in block: continue
#             for line in block["lines"]:
#                 line_text = "".join(span["text"] for span in line["spans"]).strip()
#                 if heading_text in line_text:
#                     y_pos = round(line["bbox"][1], 1)
#                     heading_indices.append((page_num, y_pos))
#                     found = True
#                     break
#             if found: break
#         if not found:
#             heading_indices.append((page_num, 0))
#     for idx, ((page_num, y_pos), heading) in enumerate(zip(heading_indices, headings)):
#         next_page_num, next_y_pos = heading_indices[idx+1] if idx+1 < len(heading_indices) else (None, None)
#         chunk = []
#         p = page_num
#         while True:
#             page = doc[p]
#             blocks = page.get_text("dict")['blocks']
#             for block in blocks:
#                 if "lines" not in block: continue
#                 for line in block["lines"]:
#                     line_y = round(line["bbox"][1], 1)
#                     if p == page_num and line_y < y_pos:
#                         continue
#                     if next_page_num is not None:
#                         if (p == next_page_num and line_y >= next_y_pos):
#                             break  # stop at next heading on next page
#                         if (p > next_page_num):
#                             break
#                     line_text = " ".join(span['text'].strip() for span in line["spans"] if span["text"].strip())
#                     chunk.append(line_text)
#             if next_page_num is not None and p == next_page_num:
#                 break
#             if p+1 >= len(doc):
#                 break
#             if next_page_num is not None and p+1 > next_page_num:
#                 break
#             p += 1
#         body = "\n".join(chunk).strip()
#         if len(body) > max_section_length:
#             body = body[:max_section_length] + '...'
#         if body:
#             results.append({
#                 'heading': heading['text'],
#                 'page': heading['page'],
#                 'chunk': body
#             })
#     doc.close()
#     return results

# def rank_sections_for_persona(sections, persona, job, model_name='all-MiniLM-L6-v2'):
#     model = SentenceTransformer("my_local_sbert")
#     query = f"{persona}. {job}"
#     section_texts = [section['chunk'] for section in sections]
#     section_embs = model.encode(section_texts, convert_to_tensor=True)
#     query_emb = model.encode([query], convert_to_tensor=True)
#     sims = st_util.cos_sim(query_emb, section_embs).cpu().numpy().flatten()
#     for i, section in enumerate(sections):
#         section['similarity'] = float(sims[i])
#     ranked = sorted(sections, key=lambda s: s['similarity'], reverse=True)
#     return ranked

# def make_final_output(input_files, persona, job, ranked_sections, top_k=5):
#     now = datetime.now().isoformat()
#     output = {
#         "metadata": {
#             "input_documents": [os.path.basename(f) for f in input_files],
#             "persona": persona,
#             "job_to_be_done": job,
#             "processing_timestamp": now
#         },
#         "extracted_sections": [],
#         "subsection_analysis": []
#     }
#     for rank, s in enumerate(ranked_sections[:top_k], 1):
#         output["extracted_sections"].append({
#             "document": os.path.basename(input_files[0]),  # for each doc, if multi-doc, use s['document']
#             "page_number": s['page'],
#             "section_title": s['heading'],
#             "importance_rank": rank
#         })
#         output["subsection_analysis"].append({
#             "document": os.path.basename(input_files[0]),
#             "section_title": s['heading'],
#             "refined_text": s['chunk'],
#             "page_number": s['page']
#         })
#     return output

# if __name__ == "__main__":
#     # --- Choose your input directory ---
#     input_directory = r"C:\Users\bhart\Downloads\Coding\Python\contest\Adobe-India-Hackathon25-main\Challenge_1b\Collection 1\PDFs"
#     output_directory = r"C:\Users\bhart\Downloads\Coding\Python\contest\app\output"
#     os.makedirs(input_directory, exist_ok=True)
#     os.makedirs(output_directory, exist_ok=True)

#     print("Batch Persona-Driven Document Intelligence")
#     print("="*60)
#     persona = input("Enter persona: ").strip()
#     job = input("Enter job to be done: ").strip()
#     pdf_files = [f for f in os.listdir(input_directory) if f.lower().endswith('.pdf')]
#     if not pdf_files:
#         print("No PDF files found.")
#         exit(1)

#     extractor = PDFStructureExtractor()

#     for pdf_fn in pdf_files:
#         pdf_path = os.path.join(input_directory, pdf_fn)
#         doc_struct = extractor.extract_document_structure(pdf_path)
#         headings = doc_struct['outline']

#         if not headings:
#             print(f"No headings found in {pdf_fn}, skipping.")
#             continue

#         sections = extract_section_chunks(pdf_path, headings)
#         ranked_sections = rank_sections_for_persona(sections, persona, job)

#         result_json = make_final_output([pdf_path], persona, job, ranked_sections, top_k=5)
#         out_fn = os.path.splitext(pdf_fn)[0] + "_challenge1b_output.json"
#         out_path = os.path.join(output_directory, out_fn)
#         with open(out_path, "w", encoding="utf-8") as f:
#             json.dump(result_json, f, indent=2, ensure_ascii=False)
#         print(f"Processed {pdf_fn} -> {out_fn}")

#     print("All done.")

import os, json, re
from datetime import datetime
from sentence_transformers import SentenceTransformer, util as st_util
from pdf_extractor import PDFStructureExtractor      # <- your provided extractor
import fitz

def extract_section_chunks(pdf_path, headings, max_section_length=4000):
    doc = fitz.open(pdf_path)
    results = []
    # Find heading locations
    heading_indices = []
    for heading in headings:
        page_num = heading['page'] - 1
        heading_text = heading['text']
        found = False
        page = doc[page_num]
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block: continue
            for line in block["lines"]:
                line_text = "".join(span["text"] for span in line["spans"]).strip()
                if heading_text in line_text:
                    y_pos = round(line["bbox"][1], 1)
                    heading_indices.append((page_num, y_pos))
                    found = True
                    break
            if found: break
        if not found:
            heading_indices.append((page_num, 0))
    for idx, ((page_num, y_pos), heading) in enumerate(zip(heading_indices, headings)):
        next_page_num, next_y_pos = heading_indices[idx+1] if idx+1 < len(heading_indices) else (None, None)
        chunk = []
        p = page_num
        while True:
            page = doc[p]
            blocks = page.get_text("dict")['blocks']
            for block in blocks:
                if "lines" not in block: continue
                for line in block["lines"]:
                    line_y = round(line["bbox"][1], 1)
                    if p == page_num and line_y < y_pos:
                        continue
                    if next_page_num is not None:
                        if (p == next_page_num and line_y >= next_y_pos): break
                        if (p > next_page_num): break
                    line_text = " ".join(span['text'].strip() for span in line["spans"] if span["text"].strip())
                    chunk.append(line_text)
            if next_page_num is not None and p == next_page_num: break
            if p+1 >= len(doc): break
            if next_page_num is not None and p+1 > next_page_num: break
            p += 1
        body = "\n".join(chunk).strip()
        if len(body) > max_section_length:
            body = body[:max_section_length] + '...'
        if body:
            results.append({
                'document': os.path.basename(pdf_path),
                'heading': heading['text'],
                'page': heading['page'],
                'chunk': body
            })
    doc.close()
    return results

def rank_sections_for_persona(sections, persona, job, model_path):
    model = SentenceTransformer(model_path)
    query = f"{persona}. {job}"
    section_texts = [section['chunk'] for section in sections]
    section_embs = model.encode(section_texts, convert_to_tensor=True, show_progress_bar=False)
    query_emb = model.encode([query], convert_to_tensor=True)
    sims = st_util.cos_sim(query_emb, section_embs).cpu().numpy().flatten()
    for i, section in enumerate(sections):
        section['similarity'] = float(sims[i])
    ranked = sorted(sections, key=lambda s: s['similarity'], reverse=True)
    return ranked

def make_final_output(input_files, persona, job, ranked_sections, top_k=10):
    now = datetime.now().isoformat()
    output = {
        "metadata": {
            "input_documents": [os.path.basename(f) for f in input_files],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": now
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }
    for rank, s in enumerate(ranked_sections[:top_k], 1):
        output["extracted_sections"].append({
            "document": s["document"],
            "page_number": s['page'],
            "section_title": s['heading'],
            "importance_rank": rank
        })
        output["subsection_analysis"].append({
            "document": s["document"],
            "section_title": s['heading'],
            "refined_text": s['chunk'],
            "page_number": s['page']
        })
    return output


if __name__ == "__main__":
    INPUT_DIR = "ollection 1\PDFs"
    OUTPUT_FILE = "challenge1b_output.json"
    MODEL_PATH = "my_local_sbert"    # Must point to a local directory

    persona = input("Enter persona: ").strip()
    job = input("Enter job to be done: ").strip()

    pdf_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("No PDF files found.")
        exit(1)

    extractor = PDFStructureExtractor()
    all_sections = []

    for pdf_path in pdf_files:
        doc_struct = extractor.extract_document_structure(pdf_path)
        headings = doc_struct['outline']
        if not headings:
            print(f"No headings found in {os.path.basename(pdf_path)}, skipping.")
            continue
        sections = extract_section_chunks(pdf_path, headings)
        all_sections.extend(sections)

    if not all_sections:
        print("No sections were found in any PDF.")
        exit(1)

    # Global ranking across all section-chunks from all PDFs
    ranked_sections = rank_sections_for_persona(all_sections, persona, job, MODEL_PATH)
    result_json = make_final_output(pdf_files, persona, job, ranked_sections, top_k=10)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=2, ensure_ascii=False)
    print(f"Saved combined output to {OUTPUT_FILE}")
