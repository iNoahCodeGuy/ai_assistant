from typing import List, Dict
import pandas as pd

class CareerKnowledgeBase:
    def __init__(self, csv_file: str):
        self.data = pd.read_csv(csv_file)

    def query(self, search_terms: List[str]) -> List[Dict]:
        results = []
        for term in search_terms:
            filtered_data = self.data[self.data.apply(lambda row: row.astype(str).str.contains(term, case=False).any(), axis=1)]
            results.extend(filtered_data.to_dict(orient='records'))
        return results

    def get_all_entries(self) -> List[Dict]:
        return self.data.to_dict(orient='records')