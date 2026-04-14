from modules.rag.loader import load_all_documents
from modules.rag.retriever import VectorStore
from modules.routing.router import detect_intent, filter_docs_by_intent
from modules.llm.ollama import generate
from modules.sentiment.sentiment import analyze_sentiment
from modules.multilingual import detect_language, translate_to_english, translate_from_english

# -----------------------------
# LOAD DATA
# -----------------------------
docs = load_all_documents()
vector_store = VectorStore(docs)

print("✅ Chatbot Ready (type 'exit' to quit)\n")

while True:
    query = input("You: ")

    if query.lower() == "exit":
        break

    # -----------------------------
    # LANGUAGE DETECTION
    # -----------------------------
    lang = detect_language(query)

    # Translate if needed
    query_en = translate_to_english(query) if lang != "en" else query

    # -----------------------------
    # SENTIMENT ANALYSIS
    # -----------------------------
    sentiment = analyze_sentiment(query_en)

    # -----------------------------
    # INTENT DETECTION
    # -----------------------------
    intent = detect_intent(query_en)

    # -----------------------------
    # RETRIEVAL
    # -----------------------------
    results = vector_store.search(query_en)
    filtered = filter_docs_by_intent(results, intent)

    context = "\n".join(filtered[:5])

    # -----------------------------
    # SMART INSTRUCTION
    # -----------------------------
    if "summarize" in query_en.lower():
        instruction = "Summarize the content clearly."
    elif "explain" in query_en.lower():
        instruction = "Explain the concept in simple terms."
    else:
        instruction = "Answer clearly and concisely."

    # -----------------------------
    # SENTIMENT ADJUSTMENT
    # -----------------------------
    if sentiment == "negative":
        instruction += " The user seems concerned. Respond in a supportive and empathetic tone."
    elif sentiment == "positive":
        instruction += " Respond in a friendly and encouraging tone."

    # -----------------------------
    # FINAL PROMPT
    # -----------------------------
    prompt = f"""
    You are a strict AI assistant.

    RULES:
    - Answer ONLY the question
    - No puzzles
    - No extra examples
    - No stories
    - If unsure, say: "I don't know"

    Context:
    {context}

    Question:
    {query_en}

    Answer:
    """

    # -----------------------------
    # GENERATE RESPONSE
    # -----------------------------
    response_en = generate(prompt)

    # Translate back if needed
    response = translate_from_english(response_en, lang) if lang != "en" else response_en

    print("\n🤖:", response)
    print("\n---\n")