# 🤖 AI Multi-Domain Chatbot with Concept Visualization

## 🚀 Overview

This project is an advanced AI chatbot capable of:

* Answering complex domain-specific questions (based on arXiv dataset)
* Multilingual interaction (auto language detection + translation)
* Image understanding using Google Gemini API
* Concept extraction using LLM (Mistral via Ollama)
* Dynamic **Knowledge Graph Visualization**

---

## 🧠 Key Features

### 🔹 1. Domain Expert Chatbot

* Uses RAG (Retrieval-Augmented Generation)
* Trained on arXiv research papers
* Handles follow-up questions

### 🔹 2. Multilingual Support

* Automatic language detection
* Supports multiple languages (Tamil, Hindi, etc.)
* Translates input/output seamlessly

### 🔹 3. Multimodal Capabilities

* Image input understanding (Gemini API)
* Text + image combined reasoning

### 🔹 4. Concept Visualization (🔥 Highlight)

* Extracts key concepts using LLM
* Builds a knowledge graph dynamically
* Shows relationships like:

  * "uses"
  * "contains"
  * "depends on"

### 🔹 5. Research Explorer

* Search and retrieve relevant research content

---

## 🛠️ Tech Stack

* Streamlit
* Python
* Ollama (Mistral LLM)
* FAISS (Vector DB)
* Google Gemini API
* NetworkX (Graph Visualization)

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📊 Example Queries

* Explain Transformers
* Explain Artificial Intelligence
* What is Machine Learning?
* Upload an image → get description

---

## 🎯 Outcome

A chatbot that:

* Explains complex research concepts
* Handles multilingual queries
* Generates real-time concept graphs

---

## 👤 Author

A. Muthu Aravind
