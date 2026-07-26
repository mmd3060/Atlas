"""
Governance Rules — Thresholds and constants for memory governance.
"""


class GovernanceRules:
    """
    Configurable thresholds for governance decisions.
    """

    def __init__(self, config=None):
        config = config or {}

        self.quality_threshold = config.get("quality_threshold", 0.6)
        self.confidence_threshold = config.get("confidence_threshold", 0.5)
        self.promote_threshold = config.get("promote_threshold", 0.85)
        self.archive_max_quality = config.get("archive_max_quality", 0.3)
        self.archive_max_confidence = config.get("archive_max_confidence", 0.3)
        self.archive_min_age_days = config.get("archive_min_age_days", 7)
        self.delete_access_threshold = config.get("delete_access_threshold", 0)
