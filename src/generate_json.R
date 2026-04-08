# 1. Load dependencies
# Use 'jsonlite' for clean JSON export
if (!require("jsonlite")) install.packages("jsonlite")
library(jsonlite)

# 2. Simulate or pull your analysis results
# This is where your Jaccard score and pathway data would live
analysis_results <- list(
  gene = "STAT3",
  condition = "Glioblastoma Multiforme",
  jaccard_score = 0.42,      # From your overlap coefficient calculation
  p_value = 0.00012,         # Statistical significance of the intersection
  overlap_count = 15,        # Number of shared pathways found
  pathway_id = "R-HSA-9006934", 
  species_comparison = "Human-Mouse",
  analysis_date = format(Sys.Date(), "%Y-%m-%d")
)

# 3. Define the output path
# We use a relative path to keep it portable within your project structure
output_path <- "data/reports/latest_discovery.json"

# 4. Create the directory if it doesn't exist
if (!dir.exists("data/reports")) {
  dir.create("data/reports", recursive = TRUE)
}

# 5. Export to JSON
# 'pretty = TRUE' makes it human-readable (good for debugging)
# 'auto_unbox = TRUE' prevents single values from being turned into arrays
write_json(
  analysis_results, 
  path = output_path, 
  pretty = TRUE, 
  auto_unbox = TRUE
)

cat("✅ Success! Genomic discovery data saved to:", output_path, "\n")