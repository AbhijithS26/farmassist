
from farming_kb import get_collection
def retrieve_documents(question, crop=None, top_k=3):
    """
    Search ChromaDB for agricultural information
    relevant to the farmer's question.
    """

    collection = get_collection()

    query = question

    if crop:
        query = f"{crop} {question}"

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved = []

    for i, document in enumerate(documents):

        metadata = metadatas[i] if i < len(metadatas) else {}
        distance = distances[i] if i < len(distances) else None

        retrieved.append({
            "document": document,
            "crop": metadata.get("crop", ""),
            "source": metadata.get("source", "Unknown"),
            "distance": distance
        })

    return retrieved


def build_context(retrieved_documents):
    """
    Convert retrieved documents into a context string
    that will be passed to the LLM.
    """

    if not retrieved_documents:
        return "No relevant agricultural information was found."

    context_parts = []

    for index, item in enumerate(retrieved_documents, start=1):

        context_parts.append(
            f"""
SOURCE {index}
Crop: {item['crop']}
Source: {item['source']}

{item['document']}
"""
        )

    return "\n".join(context_parts)
