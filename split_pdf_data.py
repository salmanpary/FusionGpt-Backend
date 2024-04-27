from langchain_text_splitters import RecursiveCharacterTextSplitter
from load_pdf_data import load_pdf_pages

def split_pdf_data(file_path):
    pages=load_pdf_pages(file_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=20)
    splitted_text=splitter.split_documents(pages)
    return splitted_text

def combine_pdf_data(file_paths):
    combined_data=[]
    for file_path in file_paths:
        print(split_pdf_data(file_path))
        combined_data+=split_pdf_data(file_path)
    print(combined_data) 
    return combined_data