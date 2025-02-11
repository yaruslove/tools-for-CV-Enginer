import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from yolo_processor import YOLOResultsProcessor

class YOLOVisualizer:
    def __init__(self, config_path: str):
        """Initialize visualizer with config file."""
        self.processor = YOLOResultsProcessor(config_path)
        self.metrics = [
            'train/box_loss', 'train/cls_loss', 'train/dfl_loss',
            'metrics/precision(B)', 'metrics/recall(B)',
            'metrics/mAP50(B)', 'metrics/mAP50-95(B)',
            'val/box_loss', 'val/cls_loss', 'val/dfl_loss',
            'lr/pg0', 'lr/pg1', 'lr/pg2'
        ]
        self.plot_types = ['normal', 'log', 'ema']
        self.MIN_ALPHA = 0.01  # Минимальное значение для alpha

    def calculate_ema(self, data: pd.Series, alpha: float) -> pd.Series:
        """Calculate Exponential Moving Average."""
        # Проверяем и корректируем alpha
        alpha = max(self.MIN_ALPHA, alpha)
        return data.ewm(alpha=alpha, adjust=False).mean()

    def create_plot(self, data: dict, metric: str, plot_type: str, ema_alpha: float = 0.1) -> go.Figure:
        """Create plot for specific metric with selected transformation."""
        fig = go.Figure()
        
        for exp_name, df in data.items():
            y_values = df[metric].copy()
            
            if plot_type == 'log':
                if (y_values <= 0).any():
                    min_positive = y_values[y_values > 0].min() if not y_values[y_values > 0].empty else 1e-10
                    y_values = y_values.clip(lower=min_positive)
            elif plot_type == 'ema':
                y_values = self.calculate_ema(y_values, ema_alpha)
            
            fig.add_trace(go.Scatter(
                x=df['epoch'],
                y=y_values,
                name=exp_name,
                mode='lines',
                line=dict(width=2),
                hovertemplate=f"epoch=%{{x}}<br>{metric}=%{{y:.4f}}<extra>{exp_name}</extra>"
            ))
        
        fig.update_layout(
            title=f'{metric} vs Epoch',
            xaxis_title='Epoch',
            yaxis_title=metric,
            height=600,
            yaxis_type='log' if plot_type == 'log' else 'linear',
            legend=dict(
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                bgcolor="rgba(255, 255, 255, 0.8)",  # Полупрозрачный белый фон
                bordercolor="rgba(0, 0, 0, 0.3)",    # Светло-серая рамка
                borderwidth=1
            )
        )
        return fig

    def run(self):
        """Run the Streamlit application."""
        st.title('YOLO Training Results Analysis')

        # Display summary table
        st.header('Summary Table')
        summary_df = self.processor.create_summary_table()
        st.dataframe(summary_df)

        # Display plots
        st.header('Training Metrics')
        data = self.processor.get_training_data()

        # Global plot type selection
        st.subheader("Global Plot Settings")
        global_plot_type = st.radio(
            "Select plot type for all graphs:",
            options=self.plot_types,
            horizontal=True,
            key="global_plot_type"
        )
        
        # Show EMA slider only when EMA is selected
        global_ema_alpha = 0.1
        if global_plot_type == 'ema':
            global_ema_alpha = st.slider(
                "EMA smoothing",
                min_value=self.MIN_ALPHA,  # Используем минимальное значение
                max_value=1.0,
                value=0.1,
                step=0.01,
                help="Higher values give more weight to recent data (less smoothing). Minimum value is 0.01"
            )

        # Plot each metric
        for metric in self.metrics:
            st.subheader(f'{metric} Plot')
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Local plot type selection
                plot_type = st.radio(
                    "Plot type",
                    options=self.plot_types,
                    horizontal=True,
                    key=f"plot_type_{metric}",
                    index=self.plot_types.index(global_plot_type)
                )
                
                # Show EMA slider only when EMA is selected
                ema_alpha = global_ema_alpha
                if plot_type == 'ema':
                    ema_alpha = st.slider(
                        "EMA smoothing",
                        min_value=self.MIN_ALPHA,  # Используем минимальное значение
                        max_value=1.0,
                        value=global_ema_alpha,
                        step=0.01,
                        key=f"ema_alpha_{metric}",
                        help="Higher values give more weight to recent data (less smoothing). Minimum value is 0.01"
                    )

            # Plot
            fig = self.create_plot(data, metric, plot_type, ema_alpha)
            st.plotly_chart(fig, use_container_width=True)

            # Add horizontal line for better separation
            st.markdown("---")

if __name__ == '__main__':
    visualizer = YOLOVisualizer('config.yaml')
    visualizer.run()