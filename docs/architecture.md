# Agentic RAG Architecture

This document outlines the 100% free deployment architecture for the Agentic RAG chatbot. Since the project is geared towards learning and research, the system simplifies the infrastructure by hosting both the frontend UI and the self-hosted reasoning hub on a single centralized Oracle VM, while continuing to offload state to managed cloud databases.

## System Diagram

```mermaid
flowchart TD
    %% Styling Definitions
    classDef user fill:#e1bee7,stroke:#8e24aa,stroke-width:2px;
    classDef oracle fill:#ffe0b2,stroke:#f57c00,stroke-width:2px;
    classDef models fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px,stroke-dasharray: 5 5;
    classDef db fill:#c8e6c9,stroke:#388e3c,stroke-width:2px;

    User((User)):::user

    subgraph Oracle_Tier ["Tier 1: Frontend, Compute & Reasoning Hub (Oracle ARM VM - 24GB RAM)"]
        UI["Chatbot UI<br>(Streamlit)"]:::oracle
        Orchestrator["Orchestration Layer API<br>(FastAPI + LangGraph)"]:::oracle
        ETL["Data Pipeline<br>(Offline Document Ingestion)"]:::oracle
        
        subgraph Local_AI ["Local AI Subsystem"]
            LLM["Reasoning Engine<br>(Ollama: gemma-4-e4b)"]:::models
            Embedder["Embedding Engine<br>(Ollama: nomic-embed-text)"]:::models
        end
    end

    subgraph Managed_Tier ["Tier 2: Managed Data Stores (Cloud Free Tiers)"]
        Neo4j[("Graph Database<br>(Neo4j AuraDB)")]:::db
        Qdrant[("Vector Database<br>(Qdrant Cloud)")]:::db
    end

    %% User Flow
    User <-->|Chat Input/Output| UI
    UI <-->|Local REST API| Orchestrator

    %% Real-Time Orchestration Flow
    Orchestrator <-->|1. Multi-step Reasoning| LLM
    Orchestrator <-->|2. Execute Cypher| Neo4j
    Orchestrator <-->|3. Semantic Search| Qdrant

    %% Offline ETL Flow
    ETL -->|Generate Embeddings| Embedder
    Embedder -->|Upload Vectors| Qdrant
    ETL <-->|Extract Graph Entities| LLM
    ETL -->|Upload Nodes/Edges| Neo4j
```
