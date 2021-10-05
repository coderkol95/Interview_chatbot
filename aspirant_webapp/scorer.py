from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

bert = SentenceTransformer('bert-large-nli-stsb-mean-tokens')

with open(r'C:\Users\ADMIN\Documents\Codebase\interview_chatbot\aspirant_webapp\count.pkl','rb') as f1:
    count = pickle.load(f1)

with open(r'C:\Users\ADMIN\Documents\Codebase\interview_chatbot\aspirant_webapp\model.pkl','rb') as f2:
    model = pickle.load(f2)

def scored(
    a: str
    ,b: str):

    bert_dist = cosine_similarity(bert.encode([a]).reshape(1,-1), bert.encode([b]).reshape(1,-1))

    count_dist = cosine_similarity(count.transform([a]).reshape(1,-1), count.transform([a]).reshape(1,-1))

    print('bert',bert_dist)
    print('count',count_dist)
    
    dists = [[count_dist[0][0],bert_dist[0][0]]]
    print(dists)
    d = model.predict(dists)

    return d
