from typing import List, Dict, Any
import json

class Output:
    def __init__(self, transaction_id: str, extracted_entity: List[str], entity_type: List[str], 
                 risk_score: float, supporting_evidence: List[str], confidence_score: float, reason: str, **kwargs):
        """
        Initialize an Output object for transaction entity analysis.

        :param transaction_id: Unique transaction identifier
        :param extracted_entity: List of entity names
        :param entity_type: List of classifications (e.g., Corporation, Shell Company)
        :param risk_score: Risk level (0-1 scale)
        :param supporting_evidence: List of data sources
        :param confidence_score: AI model confidence (0-1 scale)
        :param reason: Explanation of the classification
        :param kwargs: Additional optional attributes
        """
        self.transaction_id = transaction_id
        self.extracted_entity = extracted_entity
        self.entity_type = entity_type
        self.risk_score = risk_score
        self.supporting_evidence = supporting_evidence
        self.confidence_score = confidence_score
        self.reason = reason

        # Store any additional attributes dynamically
        self.additional_properties = kwargs  

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the object to a dictionary, including extra properties.
        """
        base_dict = {
            "Transaction ID": self.transaction_id,
            "Extracted Entity": self.extracted_entity,
            "Entity Type": self.entity_type,
            "Risk Score": self.risk_score,
            "Supporting Evidence": self.supporting_evidence,
            "Confidence Score": self.confidence_score,
            "Reason": self.reason
        }
        # Merge with additional properties
        base_dict.update(self.additional_properties)
        return base_dict

    def to_json(self) -> str:
        """
        Convert the object to a JSON string.
        """
        return json.dumps(self.to_dict(), indent=4)
