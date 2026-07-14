# Autonomous AI Procurement Agent

A lightweight, end-to-end AI agentic workflow designed for Demand-to-Pay (D2P) and Procurement operations. This project demonstrates modern GenAI integration without relying on heavy frontend frameworks.

## 🚀 Features
* **Agentic AI Workflow:** Utilizes Gemini's Function Calling (Tools) to autonomously calculate order costs based on dynamic inventory data.
* **FastAPI Backend:** High-performance RESTful API serving both data endpoints and LLM orchestrations.
* **Responsive Vanilla UI:** Clean, asynchronous JavaScript frontend (`fetch` API) embedded directly via static mounting.
* **Context-Aware RAG:** Retrieves real-time stock quantities and pricing from a local CSV database to ground the AI's responses.

## 🛠️ Tech Stack
* **Backend:** Python, FastAPI, Uvicorn, Pydantic
* **AI/LLM:** Google Generative AI (Gemini 1.5/2.5 Flash), Prompt Engineering
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Data:** Pandas / Python CSV Module
