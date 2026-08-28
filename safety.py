HIGH_RISK_KEYWORDS = [

    "pesticide",
    "insecticide",
    "fungicide",
    "herbicide",
    "dosage",
    "dose",
    "spray",

    "பூச்சிக்கொல்லி",
    "மருந்து",
    "அளவு",
    "தெளிக்க",

    "कीटनाशक",
    "दवा",
    "मात्रा",
    "छिड़काव"
]


def contains_high_risk_request(question):
    """
    Detect potentially high-risk chemical-treatment questions.
    """

    question_lower = question.lower()

    for keyword in HIGH_RISK_KEYWORDS:
        if keyword.lower() in question_lower:
            return True

    return False


def assess_confidence(retrieved_documents):

    if not retrieved_documents:
        return 0.0

    count = len(retrieved_documents)

    if count >= 3:
        return 0.85

    if count == 2:
        return 0.70

    return 0.55


def apply_safety_rules(question, retrieved_documents):

    high_risk = contains_high_risk_request(question)
    confidence = assess_confidence(retrieved_documents)

    if not retrieved_documents:
        return {
            "safe": False,
            "needs_expert": True,
            "confidence": 0.0,
            "reason": "No reliable agricultural information found."
        }

    if high_risk:
        return {
            "safe": False,
            "needs_expert": True,
            "confidence": min(confidence, 0.40),
            "reason": (
                "High-risk pesticide or treatment "
                "request requires expert verification."
            )
        }

    return {
        "safe": True,
        "needs_expert": False,
        "confidence": confidence,
        "reason": "Relevant agricultural information found."
    }


def safety_message(language):

    messages = {

        "en":
        "I don't have enough reliable information to safely answer "
        "this question. Please consult a qualified agricultural expert.",

        "ta":
        "இந்த கேள்விக்கு பாதுகாப்பாக பதிலளிக்க போதுமான நம்பகமான தகவல் "
        "இல்லை. தகுதியான வேளாண் நிபுணரை அணுகவும்.",

        "hi":
        "इस प्रश्न का सुरक्षित उत्तर देने के लिए पर्याप्त विश्वसनीय "
        "जानकारी नहीं है। कृपया कृषि विशेषज्ञ से सलाह लें।"
    }

    return messages.get(language, messages["en"])
