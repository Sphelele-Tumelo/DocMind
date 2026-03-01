
## 🧠 DocMind: AI-Powered Document Intelligence
Transforming messy paperwork into professional, actionable data.

## 🚀 Overview
DocMind is a full-stack SaaS designed to solve the "Low-Quality Scan" problem for South African businesses. It uses Deep Learning (ESRGAN) to enhance blurry document photos and FastAPI to coordinate a high-performance processing pipeline.

## 🛠️ Tech Stack
Backend: Python, FastAPI, Streamlit (Tests)

AI/ML: PyTorch, ESRGAN (Super-Resolution), Gemini-1.5-Pro (Intelligence)

Frontend: React (Moving to React Native for Mobile-First)

Database: Supabase (PostgreSQL + Auth)

Infrastructure: Docker, Render/Vercel

## ✨ Key Features
Auto-Enhance: Automatically cleans up "WhatsApp-style" document photos using Super-Resolution.

The Portfolio Bundle (In-Dev): Merges ID, CV, and Bank Statements into a single, optimized, "Job-Ready" PDF.

Smart Extract: Uses RAG (Retrieval-Augmented Generation) to answer questions about uploaded documents.

## 🏗️ Architecture
I built this using a Microservices approach to ensure that the heavy AI processing doesn't block the user interface. By using RabbitMQ, the system can handle multiple document uploads simultaneously without crashing.

[......70% done ] Theres more stick around :)



