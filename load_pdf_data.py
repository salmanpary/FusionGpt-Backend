from langchain_community.document_loaders import PyPDFLoader

def load_pdf_pages(file_path):
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        return pages
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return None