import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# 1. Load your analyzed data
df = pd.read_csv('magicbricks_bangalore_final_with_rent.csv')

# 2. Create the Search String
# We combine title and location so the search is context-aware
df['search_text'] = df['title'] + " located in " + df['location']

# 3. Initialize the Embedding Model
# 'all-MiniLM-L6-v2' is fast and perfect for local development
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Generating embeddings... This might take a minute.")
embeddings = model.encode(df['search_text'].tolist(), show_progress_bar=True)

# 4. Create the FAISS Index
dimension = embeddings.shape[1]  # This will be 384
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype('float32'))

# 5. Save the index and the data for the next step
faiss.write_index(index, "property_index.faiss")
# We save the dataframe to match the index IDs back to property details later
df.to_csv("data/metadata.csv", index=False)

print("Success! 'property_index.faiss' and 'metadata.csv' have been created.")