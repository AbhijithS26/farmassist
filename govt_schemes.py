import chromadb

SCHEMES_CHROMA_PATH = "./chroma_db_schemes"
SCHEMES_COLLECTION_NAME = "govt_schemes"


def get_schemes_chroma_client():
    """
    Create or open a persistent ChromaDB client for schemes.
    """
    return chromadb.PersistentClient(path=SCHEMES_CHROMA_PATH)


def get_schemes_collection():
    """
    Get the government schemes collection.
    """
    client = get_schemes_chroma_client()

    collection = client.get_or_create_collection(
        name=SCHEMES_COLLECTION_NAME,
        metadata={
            "description": "Tamil Nadu Government Agricultural Schemes"
        }
    )

    return collection

SCHEMES = [
    {
        "id": "tn_km_subsidy",
        "scheme_name": "Tamil Nadu Krishi Mitra Subsidy Scheme",
        "crop": "all",
        "text": """
        Tamil Nadu Krishi Mitra Subsidy Scheme

        Description: This scheme provides financial assistance to farmers for purchasing agricultural equipment, seeds, and fertilizers.
        Eligibility: All farmers in Tamil Nadu with valid land ownership documents.
        Benefits: Up to 50% subsidy on agricultural equipment, 30% on seeds, and 20% on fertilizers.
        Application Process: Apply online through the Tamil Nadu Agriculture Department portal or visit the nearest Agricultural Extension Center.
        Required Documents: Land records, Aadhaar card, bank passport, and passport-sized photos.
        """,
    },
    {
        "id": "tn_paddy_insurance",
        "scheme_name": "Tamil Nadu Paddy Crop Insurance Scheme",
        "crop": "rice",
        "text": """
        Tamil Nadu Paddy Crop Insurance Scheme

        Description: Provides insurance coverage for paddy crops against natural calamities, pests, and diseases.
        Eligibility: Farmers cultivating paddy in notified areas of Tamil Nadu.
        Benefits: Compensation for crop loss up to 75% of the sum insured.
        Premium: Heavily subsidized by the government; farmer pays only a nominal premium.
        Application Process: Enrollment through Primary Agricultural Cooperative Societies (PACS) or online via the Tamil Nadu Crop Insurance Portal.
        Required Documents: Land cultivation certificate, sowing details, and identity proof.
        """,
    },
    {
        "id": "tn_organic_farming",
        "scheme_name": "Tamil Nadu Organic Farming Promotion Scheme",
        "crop": "all",
        "text": """
        Tamil Nadu Organic Farming Promotion Scheme

        Description: Encourages farmers to adopt organic farming practices through financial and technical support.
        Eligibility: Farmers willing to convert to organic farming or already practicing organic farming.
        Benefits:
          - Financial assistance for organic certification (up to ₹10,000 per hectare)
          - Subsidy on organic inputs (30% on bio-fertilizers, bio-pesticides)
          - Training and extension services
        Application Process: Apply through the Tamil Nadu State Organic Certification Agency (TNSOCA) or District Agricultural Office.
        Required Documents: Land details, farming plan, and identity proof.
        """,
    },
    {
        "id": "tn_solar_pump",
        "scheme_name": "Tamil Nadu Solar Pump Set Scheme",
        "crop": "all",
        "text": """
        Tamil Nadu Solar Pump Set Scheme

        Description: Promotes the use of solar energy for irrigation by providing solar pump sets at subsidized rates.
        Eligibility: Farmers with agricultural land connection and valid water source.
        Benefits:
          - Up to 90% subsidy on solar pump sets (subject to a maximum limit)
          - Reduced electricity costs for irrigation
          - Environmentally friendly
        Application Process: Apply through the Tamil Nadu Energy Development Agency (TEDA) or online portal.
        Required Documents: Land records, water source details, and Aadhaar card.
        """,
    },
    {
        "id": "tn_market_yard",
        "scheme_name": "Tamil Nadu Agricultural Market Yard Improvement Scheme",
        "crop": "all",
        "text": """
        Tamil Nadu Agricultural Market Yard Improvement Scheme

        Description: Aims to improve agricultural market yards to ensure better prices and reduce post-harvest losses.
        Eligibility: Farmers selling produce in notified market yards.
        Benefits:
          - Improved storage facilities
          - Better auction platforms
          - Grading and packaging support
        Application Process: Benefits are automatically available to farmers selling in improved market yards.
        Required Documents: None for availing benefits; just sell produce in the market yard.
        """,
    }
]


def setup_schemes_knowledge_base():
    """
    Add starter government schemes data to ChromaDB.

    ChromaDB creates embeddings automatically using its
    default local embedding function (no external API needed).
    """
    collection = get_schemes_collection()

    documents = []
    ids = []
    metadatas = []

    for item in SCHEMES:
        ids.append(item["id"])
        documents.append(item["text"])

        metadatas.append({
            "scheme_name": item["scheme_name"],
            "crop": item["crop"],
            "source": "Tamil Nadu Government Agricultural Schemes"
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Schemes knowledge base ready: {collection.count()} documents")

    return collection


def retrieve_schemes(question, crop=None, top_k=3):
    """
    Search ChromaDB for government schemes information
    relevant to the farmer's question.
    """
    collection = get_schemes_collection()

    # If crop is selected, include it in the query.
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
            "scheme_name": metadata.get("scheme_name", ""),
            "crop": metadata.get("crop", ""),
            "source": metadata.get("source", "Unknown"),
            "distance": distance
        })

    return retrieved


def build_schemes_context(retrieved_schemes):
    """
    Convert retrieved schemes documents into a context string
    that will be passed to the LLM.
    """
    if not retrieved_schemes:
        return "No relevant government schemes information was found."

    context_parts = []

    for index, item in enumerate(retrieved_schemes, start=1):
        context_parts.append(
            f"""
SCHEME {index}
Scheme Name: {item['scheme_name']}
Crop: {item['crop']}
Source: {item['source']}

{item['document']}
"""
        )

    return "\n".join(context_parts)


if __name__ == "__main__":
    setup_schemes_knowledge_base()
