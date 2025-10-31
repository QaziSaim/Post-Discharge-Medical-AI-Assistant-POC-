import json
from typing import List, Union

def load_patient_data(file_path: str) -> List[dict]:
    with open(file_path, "r") as f:
        return json.load(f)
    
def find_patient_by_name(name: str, patient_data: List[dict]) -> Union[dict, List[dict], str]:
    matches = [p for p in patient_data if p["patient_name"].lower() == name.lower()]

    if len(matches) == 0:
        return "Patient not found!!"
    elif len(matches) == 1:
        return matches[0]
    else:
        return matches
    
if __name__ == "__main__":
    data = load_patient_data("patient_reports.json")

    input_name = input("Enter patient name: ")
    result = find_patient_by_name(input_name, data)

    print("\nLookup Result:\n")
    print(result)