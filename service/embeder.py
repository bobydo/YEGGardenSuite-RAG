

from sentence_transformers import SentenceTransformer
import platform

class QwenInstruct:
    def __init__(self, model_path):

        if platform.system() == "Windows":
            self.model = SentenceTransformer(model_name_or_path=model_path, trust_remote_code= True, device="cuda")
        elif platform.system() == "Darwin":
            self.model = SentenceTransformer(model_name_or_path=model_path, trust_remote_code= True, device="mps")
        elif platform.system() == "Linux":
            self.model = SentenceTransformer(model_name_or_path=model_path, trust_remote_code= True, device="cuda")
        else:
            self.model = SentenceTransformer(model_name_or_path=model_path, trust_remote_code= True, device="cpu")
        print(self.model.max_seq_length)  
        self.model.max_seq_length = 8192 

    def embed_documents(self, text: [str]) -> [list[float]]:
        # 嵌入文档并返回嵌入向量列表
        text_list = text
        embeddings = self.model.encode(text_list)
        return embeddings

    def embed_query(self, text: [str]) -> [list[float]]:
        text_list = text
        embeddings = self.model.encode(text_list,prompt_name='query')
        return embeddings