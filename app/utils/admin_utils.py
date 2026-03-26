class AdminUtils:
    @staticmethod
    def format_trend_data(query_results):
        """Standardizes DB results for Chart.js labels/values."""
        return {
            "labels": [r.month for r in query_results],
            "values": [float(r.avg_usage) for r in query_results]
        }