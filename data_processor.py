import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class DataProcessor:
    def __init__(self, df):
        self.df = df

    def get_area_statistics(self):
        """Calculate waste statistics by area"""
        return self.df.groupby('area')['waste_kg'].agg(['mean', 'min', 'max']).round(2)

    def create_waste_trend_plot(self):
        """Create waste trend visualization"""
        fig = px.line(
            self.df, 
            x='date', 
            y='waste_kg', 
            color='area',
            title='Tendência de Produção de Resíduos por Área'
        )
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Resíduos (kg)",
            legend_title="Área"
        )
        return fig

    def create_area_comparison_plot(self):
        """Create area comparison bar chart"""
        avg_by_area = self.df.groupby('area')['waste_kg'].mean().round(2)
        fig = px.bar(
            x=avg_by_area.index, 
            y=avg_by_area.values,
            title='Média de Resíduos por Área',
            labels={'x': 'Área', 'y': 'Média de Resíduos (kg)'}
        )
        return fig

    def get_daily_summary(self):
        """Get daily waste summary"""
        return self.df.groupby('date')['waste_kg'].sum().mean().round(2)
