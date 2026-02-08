class Calculator:
    """
    Handles deterministic financial calculations.
    """

    @staticmethod
    def compute_tier1(cet1, at1):
        return cet1 + at1

    @staticmethod
    def compute_total(tier1, tier2):
        return tier1 + tier2

    @staticmethod
    def compute_ratio(num, denom):

        if denom == 0:
            return 0.0

        return round((num / denom) * 100, 2)
