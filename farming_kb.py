
import chromadb
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "agricultural_knowledge"
def get_chroma_client():
    """
    Create or open a persistent ChromaDB client.
    """
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection():
    """
    Get the agricultural knowledge collection.
    """
    client = get_chroma_client()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "KrishiMitra agricultural knowledge base"
        }
    )

    return collection

KNOWLEDGE = [

    # ---------------- RICE ----------------

    {
        "id": "rice_yellow_leaves",
        "crop": "rice",
        "text": """
        Rice / நெல் / धान

        Problem:
        Yellow leaves / இலைகள் மஞ்சள் நிறமாகுதல் / पत्तियां पीली होना

        Rice leaves becoming yellow can have multiple possible causes.
        Possible factors include nutrient problems, water management,
        pest activity, or disease.

        A single symptom should not be used to make a definite diagnosis.
        The farmer should observe crop age, field water conditions,
        leaf pattern, and other symptoms.

        For uncertain disease or pesticide decisions, consult a
        qualified agricultural officer or agricultural expert.
        """
    },

    {
        "id": "rice_water",
        "crop": "rice",
        "text": """
        Rice / நெல் / धान

        Water management:

        Rice water requirements depend on crop stage, soil conditions,
        rainfall, and local farming practices.

        Farmers should avoid making irrigation decisions based only
        on a generic schedule. Field conditions and local agricultural
        recommendations should be considered.
        """
    },

    {
        "id": "rice_pests",
        "crop": "rice",
        "text": """
        Rice / நெல் / धान

        Pest problems:

        Rice can experience different insect and pest problems.
        Before choosing a treatment, the farmer should identify the
        pest and observe the type and extent of crop damage.

        Do not recommend a pesticide or dosage without reliable,
        crop-specific and locally applicable information.
        """
    },


    # ---------------- TOMATO ----------------

    {
        "id": "tomato_leaf_curl",
        "crop": "tomato",
        "text": """
        Tomato / தக்காளி / टमाटर

        Problem:
        Leaf curling / இலை சுருட்டல் / पत्तियों का मुड़ना

        Tomato leaves curling can have multiple possible causes,
        including pest activity, water stress, temperature stress,
        or disease.

        Check the underside of leaves for insects and observe other
        symptoms before deciding on a diagnosis.

        A photograph and additional symptoms may be useful for expert
        diagnosis.
        """
    },

    {
        "id": "tomato_water",
        "crop": "tomato",
        "text": """
        Tomato / தக்காளி / टमाटर

        Water management:

        Tomato plants require appropriate moisture, but irrigation
        requirements vary with soil, weather, crop stage and local
        conditions.

        Farmers should observe soil moisture and crop condition rather
        than following an unsuitable generic irrigation schedule.
        """
    },


    # ---------------- COTTON ----------------

    {
        "id": "cotton_pests",
        "crop": "cotton",
        "text": """
        Cotton / பருத்தி / कपास

        Pest problems:

        Cotton can be affected by different insect pests.
        Farmers should first observe the insect, plant part affected,
        crop growth stage and level of damage.

        Do not guess a pesticide name or dosage. Local agricultural
        recommendations should be verified before chemical treatment.
        """
    },

    {
        "id": "cotton_leaf_damage",
        "crop": "cotton",
        "text": """
        Cotton / பருத்தி / कपास

        Leaf damage:

        Leaf damage can have several causes including insects,
        environmental stress and disease.

        Diagnosis should consider the complete set of symptoms,
        crop stage and local conditions.
        """
    }
]


def setup_knowledge_base():
    """
    Add starter agricultural knowledge to ChromaDB.

    ChromaDB creates embeddings automatically using its
    default local embedding function (no external API needed).
    """

    collection = get_collection()

    documents = []
    ids = []
    metadatas = []

    for item in KNOWLEDGE:
        ids.append(item["id"])
        documents.append(item["text"])

        metadatas.append({
            "crop": item["crop"],
            "source": "KrishiMitra starter knowledge base"
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Knowledge base ready: {collection.count()} documents")

    return collection


if __name__ == "__main__":
    setup_knowledge_base()
