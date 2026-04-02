import json

def parse_fhir_bundle(file_path):
    with open(file_path, 'r') as f:
        bundle = json.load(f)
    
    extracted_data = {
        "patient_id": None,
        "diagnoses": [],
        "labs": []
    }

    for entry in bundle.get('entry', []):
        resource = entry.get('resource', {})
        res_type = resource.get('resourceType')

        if res_type == "Patient":
            extracted_data["patient_id"] = resource.get("id")
        
        elif res_type == "Condition":
            coding = resource.get("code", {}).get("coding", [{}])[0]
            extracted_data["diagnoses"].append(coding.get("display"))
            
        elif res_type == "Observation":
            lab_name = resource.get("code", {}).get("coding", [{}])[0].get("display")
            val = resource.get("valueQuantity", {}).get("value")
            extracted_data["labs"].append(f"{lab_name}: {val}")

    return extracted_data

if __name__ == "__main__":
    data = parse_fhir_bundle("data/ehr_mock/patient_alpha.json")
    print(f"Extracted Profile: {data}")
