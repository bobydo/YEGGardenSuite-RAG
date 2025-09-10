from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

# Logs directory
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Ollama model names
GEN_MODEL = "llama3.1:8b"          # Meta Llama via Ollama (chat model)
EMBED_MODEL = "nomic-embed-text"   # Embedding model via Ollama



# Local FAISS index directory
INDEX_DIR = Path("./edmonton_backyard_faiss")

# Allowed hostnames for scraping / loading
ALLOWED = {"zoningbylaw.edmonton.ca", "www.edmonton.ca"}

# Source pages (add more official City of Edmonton pages if needed)
URLS = [
    "https://www.edmonton.ca/",
    "https://www.edmonton.ca/business_economy/permits-development-construction",
    "https://www.edmonton.ca/city_government/bylaws",
    "https://www.edmonton.ca/city_government/bylaws/zoning-bylaw",
    "https://www.edmonton.ca/programs_services/for_schools_students_teachers/post-secondary-student-resources",
    "https://www.edmonton.ca/programs_services/housing/affordable-housing-developments",
    "https://www.edmonton.ca/programs_services/housing/welcome-homes",
    "https://www.edmonton.ca/projects_plans/transit/capital-line-south",
    "https://www.edmonton.ca/public-files/assets/document?path=PDF/Approved_2012-14_Capital_Budget.pdf",
    "https://www.edmonton.ca/public-files/assets/document?path=PDF/Discussion_Paper_4_North_Saskatchewan_River_Water_Quality.pdf",
    "https://www.edmonton.ca/public-files/assets/document?path=PDF/Secondary_Suite_Design_Guide.pdf",
    "https://www.edmonton.ca/public-files/assets/document?path=PDF/current_Zoning_Bylaw.pdf",
    "https://www.edmonton.ca/public-files/assets/document?path=Residential_Landscaping_and_Hardsurfacing_Requirements.pdf",
    "https://www.edmonton.ca/residential-neighbourhoods",
    "https://www.edmonton.ca/residential_neighbourhoods/application-requirements-house-permits",
    "https://www.edmonton.ca/residential_neighbourhoods/backyard-housing",
    "https://www.edmonton.ca/residential_neighbourhoods/develop-your-property",
    "https://www.edmonton.ca/residential_neighbourhoods/lot_grading/surface-drainage-problems-faq",
    "https://www.edmonton.ca/residential_neighbourhoods/residential-construction",
    "https://www.edmonton.ca/residential_neighbourhoods/secondary-suites",
    "https://www.edmonton.ca/residential_neighbourhoods/uncovered-deck",
    "https://www.edmonton.ca/sites/default/files/public-files/assets/ProvincialFCSSMeasuresBank.xlsx?cb=1687494504",
    "https://zoningbylaw.edmonton.ca/backyard-housing",
    "https://zoningbylaw.edmonton.ca/bylaw-pdf-print",
    "https://zoningbylaw.edmonton.ca/dc-20974",
    "https://zoningbylaw.edmonton.ca/dc-21145",
    "https://zoningbylaw.edmonton.ca/dc-21276",
    "https://zoningbylaw.edmonton.ca/dc1-15946",
    "https://zoningbylaw.edmonton.ca/dc1-20476",
    "https://zoningbylaw.edmonton.ca/driveway",
    "https://zoningbylaw.edmonton.ca/flanking-side-yard",
    "https://zoningbylaw.edmonton.ca/home",
    "https://zoningbylaw.edmonton.ca/part-2-standard-zones-and-overlays",
    "https://zoningbylaw.edmonton.ca/part-2-standard-zones-and-overlays/commercial-zones/2100-cg-general-commercial-zone",
    "https://zoningbylaw.edmonton.ca/part-2-standard-zones-and-overlays/residential-zones/210-rs-small-scale-residential-zone",
    "https://zoningbylaw.edmonton.ca/part-2-standard-zones-and-overlays/residential-zones/220-rsf-small-scale-flex-residential-zone",
    "https://zoningbylaw.edmonton.ca/part-2-standard-zones-and-overlays/residential-zones/230-rsm-small-medium-scale-transition-residential-zone",
    "https://zoningbylaw.edmonton.ca/part-3-special-area-zones",
    "https://zoningbylaw.edmonton.ca/part-3-special-area-zones/paisley-special-area/3151-pld-paisley-low-density-zone",
    "https://zoningbylaw.edmonton.ca/part-5-general-development-regulations",
    "https://zoningbylaw.edmonton.ca/part-5-general-development-regulations/550-inclusive-design",
    "https://zoningbylaw.edmonton.ca/part-5-general-development-regulations/560-landscaping",
    "https://zoningbylaw.edmonton.ca/part-5-general-development-regulations/580-parking-access-site-circulation-and-bike-parking",
    "https://zoningbylaw.edmonton.ca/part-5-general-development-regulations/590-projection-setbacks",
    "https://zoningbylaw.edmonton.ca/part-6-specific-development-regulations",
    "https://zoningbylaw.edmonton.ca/part-6-specific-development-regulations/610-backyard-housing",
    "https://zoningbylaw.edmonton.ca/part-6-specific-development-regulations/660-home-based-businesses",
    "https://zoningbylaw.edmonton.ca/part-6-specific-development-regulations/690-signs",
    "https://zoningbylaw.edmonton.ca/part-8-definitions",
    "https://zoningbylaw.edmonton.ca/part-8-definitions/820-general-definitions",
    "https://zoningbylaw.edmonton.ca/setback",
    "https://zoningbylaw.edmonton.ca/street",
]

# Optional: online PDF sources (processed with OnlinePDFLoader)
PDF_URLS = [
    # Example: City "How-To Guide" PDF
    # "https://www.edmonton.ca/sites/default/files/public-files/Backyard-Housing-How-To-Guide.pdf?cb=1737052351",
]

# Optional: local PDF paths (if you download PDFs manually)
LOCAL_PDF_PATHS = [
    "./data/raw/2025-Planning-and-Development-Fee-Schedules.pdf",
    "./data/raw/2025_RES_Improved.pdf",
    "./data/raw/AgeFriendlyEdmonton-TheFirstFiveYears.pdf",
    "./data/raw/Backyard-Housing-How-To-Guide.pdf",
    "./data/raw/Detached_Garage_Design_Guide.pdf",
    "./data/raw/Downtown_Public_Places_Plan.pdf",
    "./data/raw/Downtown_Streetscape_Manual.pdf",
    "./data/raw/Downtown_Streetscape_Manual_1.pdf",
    "./data/raw/Edmonton-Zoning-Bylaw-Residential-Land-Use-Matrix.pdf",
    "./data/raw/Edmonton_Exhibition_Lands_DraftPlanningFramework.pdf",
    "./data/raw/Get-To-Know-Your-Zoning-Bylaw-Residential-Small-Scale-RS-Zone.pdf",
    "./data/raw/Housing-Information-Sessions-Boards.pdf",
    "./data/raw/Project-Implementation-Plan-Guide.pdf",
    "./data/raw/ResidentialGuidelines.pdf",
    "./data/raw/Secondary_Suite_Design_Guide.pdf",
    "./data/raw/Sheds-OtherAccessoryBuildings-LocationRestrictions.pdf",
    "./data/raw/Shed_and_Accessory_Structures_Restrictions.pdf",
    "./data/raw/TheWayAheadProgressReport_2016_FINAL.pdf",
    "./data/raw/ZBRI-MNO-Retirement.pdf",
    "./data/raw/Zoning-Bylaw-Guide.pdf",
    "./data/raw/ZoningBylawRenewal-Responses-Councillor-Questions.pdf",
] 

# System-style rules baked into the prompt
SYSTEM_RULES = (
    "You are an assistant for Edmonton backyard housing. "
    "Answer ONLY from the provided context (official City sources). "
    "If the answer is not in the context, reply exactly with: NOT_ENOUGH_CONTEXT. "
    "Be concise and non-legal. "
    "Silently fix spelling/grammar in user questions and in your answers; "
    "do not echo misspelled words. Keep intentional names as written."
)

# ---------- Ollama generation parameters (tunable) ----------
# These map to Ollama's /generate options.
# See: https://github.com/ollama/ollama/blob/main/docs/modelfile.md#parameters
LLM_KWARGS = {
    # Decoding
    "temperature": 0.3,        # lower for factual QA
    "top_k": 40,               # shortlist of candidates
    "top_p": 0.9,              # nucleus sampling
    "tfs_z": 1.0,              # tail-free sampling

    # Length & context
    "num_predict": 384,        # max new tokens to generate
    "num_ctx": 8192,           # context window tokens (depends on model)

    # Repetition control
    "repeat_last_n": 64,
    "repeat_penalty": 1.1,

    # Mirostat (advanced, keeps perplexity steady). 0 = off, 1 or 2 = on.
    "mirostat": 0,
    "mirostat_tau": 5.0,
    "mirostat_eta": 0.1,

    # Optional: set a stop sequence (example shown, usually not needed here)
    # "stop": ["\nSources:", "\nContext:"],

    # Connectivity (uncomment if your Ollama is remote)
    # "base_url": "http://localhost:11434",
}
