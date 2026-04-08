# BioMed-Agent-Framework
### *Autonomous Clinical Decision Support via Multi-Omics and Medical Text Synthesis*

## **Project Overview**
This framework is an end-to-end pipeline designed to bridge the gap between high-dimensional **Bioinformatics** and **Agentic AI**. It demonstrates a scalable infrastructure for identifying disease-state markers across species and utilizing **Medical LLMs** to synthesize clinical evidence for drug-target prioritization.

## **Core Capabilities**
* **Multimodal Data Ingestion:** Integrated handling of **scRNA-seq matrices**, **Medical Journals (PubMed)**, and **Electronic Health Records (EHR)**.
* **Representation Learning:** Utilizing **scANVI/scArches** to identify conserved markers across human and mouse manifolds for Neurodegeneration research.
* **Agentic Reasoning:** A **LangGraph-based autonomous agent** that orchestrates LLM calls to validate targets against clinical databases (Open Targets) and scientific literature.
* **Clinical Decision Support (CDS):** Automated generation of structured reports to accelerate translational discovery and medical education.

## **Directory Structure**
- `data/`: Ingestion layer for Omics, PubMed abstracts, and mock EHR.
- `src/ingestion/`: NLP-driven parsers for clinical texts (SciSpacy).
- `src/analysis/`: Logic for cross-referencing molecular and clinical data.
- `src/agents/`: The reasoning core; orchestrating autonomous LLM research loops.

## **Tech Stack**
- **AI/ML:** PyTorch, SciSpacy, LangGraph, LangChain.
- **Informatics:** Scanpy, AnnData, GraphQL (Open Targets API).
- **Infrastructure:** Modular Python architecture designed for HPC environments.

## BioMed-Agent-Framework
This framework utilizes an **Agentic Critique & Refine loop** to generate clinical reasoning memos.
- **Model:** Gemini 2.5 Flash-Lite (Optimized for high-frequency reasoning)
- **Architecture:** 3-Phase synthesis (Drafting -> Peer Review -> Finalization)
- **Resilience:** Built-in exponential backoff for API quota management.