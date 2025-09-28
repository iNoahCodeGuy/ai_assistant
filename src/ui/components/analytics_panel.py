from streamlit import st
import pandas as pd
from src.analytics.metrics_collector import MetricsCollector

class AnalyticsPanel:
    def __init__(self):
        self.metrics_collector = MetricsCollector()

    def display_metrics(self):
        st.header("Analytics Panel")
        
        # Display user interaction metrics
        st.subheader("User Interaction Metrics")
        metrics_data = self.metrics_collector.get_user_metrics()
        if metrics_data.empty:
            st.write("No metrics available.")
        else:
            st.dataframe(metrics_data)

        # Display system performance metrics
        st.subheader("System Performance Metrics")
        performance_data = self.metrics_collector.get_performance_metrics()
        if performance_data.empty:
            st.write("No performance metrics available.")
        else:
            st.dataframe(performance_data)

    def run(self):
        self.display_metrics()