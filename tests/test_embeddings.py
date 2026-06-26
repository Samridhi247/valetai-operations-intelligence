from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

v1 = model.encode("Driver could not access community - gate code expired")
v2 = model.encode("Gate access restrictions caused delay on route")
v3 = model.encode("Vehicle breakdown impacted collections")

sim_related = cosine_similarity([v1], [v2])[0][0]
sim_unrelated = cosine_similarity([v1], [v3])[0][0]

print("Similarity between two gate-related notes:", sim_related)
print("Similarity between gate note and vehicle note:", sim_unrelated)