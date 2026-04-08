# ==========================================
# 1. BASE IMAGE
# ==========================================
FROM python:3.11-slim

# ==========================================
# 2. SYSTEM DEPENDENCIES (R + Build Tools)
# ==========================================
# We install R and compilers needed for heavy Python/R libraries
RUN apt-get update && apt-get install -y \
    r-base \
    libcurl4-openssl-dev \
    libssl-dev \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# 3. R CONFIGURATION
# ==========================================
# Install jsonlite so R can export data for the Python agent
RUN R -e "install.packages('jsonlite', repos='http://cran.rstudio.com/')"

# ==========================================
# 4. PYTHON CONFIGURATION
# ==========================================
WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# 5. SOURCE CODE TRANSFER
# ==========================================
# This moves your scripts from your Mac into the /app folder
COPY generate_json.R /app/generate_json.R
COPY src /app/src

# ==========================================
# 6. EXECUTION PIPELINE
# ==========================================
# Runs the R pathway analysis first, then launches the AI agent
# Instead of a single string, we use a JSON array (Exec Form)
CMD ["/bin/sh", "-c", "Rscript generate_json.R && python src/agents/biomed_agent.py"]