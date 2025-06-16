import fitz 
import os

def extract_text_from_pdfs(pdf_dir='scraper/pdfs'):
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            path = os.path.join(pdf_dir, filename)
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            print(f"\n📄 Extracted from {filename}:\n")
            print(text[:500])
           

if __name__ == "__main__":
    extract_text_from_pdfs()
