from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
DetectorFactory.seed = 0
SUPPORTED_LANGUAGES = {
    "ta": "Tamil",
    "hi": "Hindi",
    "en": "English"
}
def detect_language(text):
    """
    Detect whether the input is Tamil, Hindi or English.

    Uses langdetect (offline, free). Falls back to English if the
    detected language isn't one we support, or detection fails
    (e.g. very short input).
    """

    try:
        detected = detect(text)
    except Exception:
        return "en"

    # langdetect uses ISO 639-1 codes; ta/hi/en match ours directly.
    if detected not in SUPPORTED_LANGUAGES:
        return "en"

    return detected


def translate_to_english(text, source_language):
    """
    Translate Tamil/Hindi input into English.
    English is returned unchanged.
    """

    if source_language == "en":
        return text

    translated = GoogleTranslator(
        source=source_language,
        target="en"
    ).translate(text)

    return translated


def translate_from_english(text, target_language):
    """
    Translate the model's English answer into the farmer's
    selected language.
    """

    if target_language == "en":
        return text

    translated = GoogleTranslator(
        source="en",
        target=target_language
    ).translate(text)

    return translated


def get_language_name(code):
    return SUPPORTED_LANGUAGES.get(code, "English")
