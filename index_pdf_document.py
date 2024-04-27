from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS 
from split_pdf_data import split_pdf_data,combine_pdf_data

embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
def index_pdf_documents(sessionid,pdf_file_names):
    all_file_paths=[f'./uploads/{pdf_file_name}' for pdf_file_name in pdf_file_names]
    print(all_file_paths)
    splitted_text=combine_pdf_data(all_file_paths)
    faiss_index=FAISS.from_documents(splitted_text,embeddings)
    faiss_index.save_local(f'./all_pdf_indexes/{sessionid}')
def get_db(session_id):
    return FAISS.load_local(f'./all_pdf_indexes/{session_id}',embeddings,allow_dangerous_deserialization=True)    