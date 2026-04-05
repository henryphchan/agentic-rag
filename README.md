# agentic-rag
Zero cost Agentic Graph RAG chatbot architecture utilizing local Gemma 4, Oracle Cloud ARM, Neo4j, and Qdrant

## 🧠 Project Overview

Traditional Agentic RAG systems rely heavily on expensive, pay-per-token cloud APIs (like OpenAI or Anthropic). This project flips that paradigm by orchestrating a **Hybrid Cloud & Local Compute Architecture**:
* **Heavy Compute & Reasoning:** Handled 100% locally on an Oracle Cloud "Always Free" ARM VM using highly quantized models (`Gemma-4-E4B`) to ensure privacy and zero inference costs.
* **State & Memory Storage:** Offloaded to managed free-tier cloud databases (Neo4j AuraDB and Qdrant Cloud) to preserve the VM's RAM exclusively for LLM inference.
* **Orchestration:** Driven by a LangGraph/FastAPI backend adhering strictly to the Single Responsibility Principle (SRP) and Dependency Inversion.


## 🏗️ Architecture & Infrastructure

This project uses a 100% free deployment architecture designed to maximize privacy and eliminate inference costs. For learning and research purposes, the compute backend, reasoning engine, and user interface all run on a single centralized machine, while persistent states are offloaded to managed cloud databases.

**Key Infrastructure:**
- **Tier 1 (Compute, UI & Reasoning):** Oracle Cloud "Always Free" ARM VM (24GB RAM, 4 OCPUs). This server locally hosts the Ollama reasoning engine (`gemma4:e4b`) and embedding engine (`nomic-embed-text`), as well as the FastAPI backend and Streamlit user interface.
- **Tier 2 (Managed Data Stores):** 
  - **Neo4j AuraDB:** Cloud graph database for storing extracted entity relationships.
  - **Qdrant Cloud:** Cloud vector database for semantic search and Retrieval-Augmented Generation (RAG).

For a detailed visual breakdown of the system components, data flows, and ETL pipelines, please refer to the **[Architecture Documentation & Diagram](docs/architecture.md)**.

## 📂 Repository Structure
The codebase is organized as a monorepo, separating concerns into isolated domains to follow software engineering best practices.
```
agentic-rag/
├── venv/                       # Virtual environment for Python dependencies
├── docs/                       # Architecture diagrams and system documentation
│
├── infrastructure/             # IaC and Server Provisioning
│   ├── setup_ubuntu_vm.sh      # Installs Python, Ollama, and pulls Gemma 4 on the Oracle VM
│   └── oracle_keep_alive.sh    # Cron job script to prevent Oracle from reclaiming the idle VM
│
├── data_pipeline/              # Offline ETL for Knowledge Graph & Vector DB Population
│   ├── extractors/             # Scripts to clean and parse raw text
│   ├── transformers/           # Chunking, vector embedding, and LLM graph extraction logic
│   └── loaders/                # Scripts to push processed data to Qdrant and Neo4j
│
├── backend/                    # Core Orchestration (Deployed on Oracle VM)
│   ├── core/                   # State definitions and environment configurations
│   ├── interfaces/             # Abstract Base Classes (Dependency Inversion Principle)
│   ├── services/               # Concrete implementations (Ollama API, Neo4j driver, Qdrant client)
│   ├── tools/                  # LLM Callable Tools (Cypher execution, Vector search)
│   ├── workflows/              # LangGraph agent loop definitions
│   ├── main.py                 # FastAPI application entrypoint
│   └── requirements.txt        # Backend dependencies
│
├── frontend/                   # User Interface (Deployed on Oracle VM alongside backend)
│   ├── app.py                  # Streamlit / Gradio application
│   └── requirements.txt        # Frontend dependencies
│
├── tests/                      # Unit and Integration Tests
│   ├── sample_data/            # Sample documents for testing
│   └── test_local_llm.py       # Validates local Ollama API connectivity
│
├── .env.example                # Template for external DB connection strings
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🛠️ Core Technologies & Design Principles
- Reasoning Engine: Gemma-4-E4B via Ollama (Running locally on ARM OCPUs).
- Graph Storage: Neo4j AuraDB (Managed Cloud).
- Vector Storage: Qdrant Cloud (Managed Cloud).
- Orchestration: LangGraph / FastAPI (Python).

## 🚀 Getting Started

### Prerequisites

Before running this project, ensure you have provisioned the following free-tier resources:

* Oracle Cloud ARM VM (Ubuntu 22.04+).
* Neo4j AuraDB Account (Save your URI, Username, and Password).
* Qdrant Cloud Account (Save your Cluster URL and API Key).

### 1. Clone & Setup Virtual Environment

SSH into your Oracle VM (remember to specify your private key with `-i` if needed) and clone the repository:

```bash
git clone https://github.com/henryphchan/agentic-rag.git
cd agentic-rag

# Create and activate an isolated Python environment
python3 -m venv venv
source venv/bin/activate

# Install all backend and frontend dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 2. Configure Environment Secrets

Copy the example environment file and add your actual database credentials.

```bash
cp .env.example .env
nano .env
```

### 3. Provision Local AI Models

If you haven't already installed Ollama and the required LLMs, you can run the provided infrastructure script:

```bash
chmod +x infrastructure/setup_ubuntu_vm.sh
./infrastructure/setup_ubuntu_vm.sh
```

Alternatively, you can manually run: `ollama pull gemma4:e4b` and `ollama pull nomic-embed-text`.

### 4. Hydrate the Databases (ETL Pipeline)

Before the agent can answer questions, it needs knowledge. Run the ETL scripts to ingest your data into the Neo4j and Qdrant databases:

> 💡 **Note:** The ETL pipeline currently supports indexing **Text (`.txt`)** and **Markdown (`.md`)** files.

**Option A: Ingest a single file**
```bash
python data_pipeline/run_pipeline.py --file tests/sample_data/sample.txt
```

**Option B: Batch ingest an entire directory**
To index all supported files within a folder recursively (defaults to `raw_data/`), use the batch ingest script:
```bash
python data_pipeline/batch_ingest.py --dir data_pipeline/raw_data
```

### 5. Start the Application

Boot up both the FastAPI backend and the Streamlit frontend gracefully:

```bash
chmod +x start_app.sh
./start_app.sh
```

### 6. Accessing the UI (Local Port Forwarding)

Because the application is running remotely on your Oracle VM, you should securely tunnel the frontend port to your local machine rather than exposing it to the public internet.

On your local computer's terminal, connect using your SSH private key to forward the port:

```bash
ssh -i /path/to/your/private_key.key -L 8501:localhost:8501 ubuntu@<your-oracle-vm-public-ip>
```

Finally, open your local browser and navigate to:
👉 http://127.0.0.1:8501

**Note:** Alternatively, you can install an RDP or VNC server on the Ubuntu VM. This allows you to remote into the Oracle Cloud VM and interact with the web interface directly from a graphical desktop environment. (The steps for installing and configuring remote desktop tools are outside the scope of this guide).

### 🧪 Testing

To verify the system's integrity, run the automated integration tests:

```bash
python tests/test_local_llm.py
python tests/test_neo4j.py
python tests/test_qdrant.py
python tests/test_etl_pipeline.py
python tests/test_tools.py
python tests/test_agent.py
python tests/test_api.py
```

For manual QA checks via the UI, refer to `tests/MANUAL_TEST_CASES.md`.
