import json
import spacy

# Harvard JD check: Handling diverse medical datasets & NLP
def parse_clinical_record(file_path):
    """
    Parses a synthetic EHR record and extracts biomedical entities.
    """
    with open(file_path, 'r') as f:
        patient_data = json.load(f)

    # Load a clinical-specific NLP model (en_core_sci_sm)
    # This identifies genes, diseases, and chemical entities
    try:
        nlp = spacy.load("en_core_sci_sm")
    except:
        return "Error: Please install scispacy and en_core_sci_sm model."

    text = patient_data['clinical_summary']
    doc = nlp(text)

    # Extracting Clinical Entities
    entities = [ent.text for ent in doc.ents]
    
    print(f"--- Processing Patient: {patient_data['patient_id']} ---")
    print(f"Extracted Medical Entities: {entities}")
    
    return {
        "id": patient_data['patient_id'],
        "entities": entities,
        "icd_code": patient_data['diagnostics']['icd_10']
    }

if __name__ == "__main__":
    # Test the parser
    parse_clinical_record("data/ehr_mock/patient_alpha.json")
