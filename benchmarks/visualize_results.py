"""
Benchmark Visualization and Reporting
=====================================

Generate professional charts and reports from benchmark results.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import argparse
from datetime import datetime

# Set style for professional charts
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


class BenchmarkVisualizer:
    """Create professional benchmark visualization charts."""
    
    def __init__(self, results_file: str, output_dir: str = "./benchmark_charts"):
        self.results_file = Path(results_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load results
        with open(self.results_file) as f:
            self.raw_results = json.load(f)
        
        self.df = pd.DataFrame(self.raw_results)
        
        # Configure plotting
        self.colors = {
            'niflheim-x': '#2E86AB',
            'langchain': '#A23B72', 
            'beeai': '#F18F01',
            'openai': '#84C7D0'
        }
        
    def create_startup_performance_chart(self) -> None:
        """Create startup performance comparison chart."""
        startup_df = self.df[self.df['category'] == 'startup']
        
        if startup_df.empty:
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('🚀 Framework Startup Performance Comparison', fontsize=16, fontweight='bold')
        
        # Agent Creation Time
        creation_time_df = startup_df[startup_df['metric'] == 'creation_time']
        if not creation_time_df.empty:
            ax = axes[0, 0]
            sns.barplot(data=creation_time_df, x='framework', y='value', hue='test_name', ax=ax)
            ax.set_title('Agent Creation Time')
            ax.set_ylabel('Time (seconds)')
            ax.set_xlabel('')
            
        # Memory Usage
        memory_df = startup_df[startup_df['metric'] == 'memory_usage']
        if not memory_df.empty:
            ax = axes[0, 1]
            sns.barplot(data=memory_df, x='framework', y='value', ax=ax)
            ax.set_title('Memory Usage During Creation')
            ax.set_ylabel('Memory (MB)')
            ax.set_xlabel('')
            
        # Comparison by Test Type
        ax = axes[1, 0]
        creation_pivot = creation_time_df.pivot_table(
            index='framework', columns='test_name', values='value', aggfunc='mean'
        )
        creation_pivot.plot(kind='bar', ax=ax)
        ax.set_title('Creation Time by Agent Type')
        ax.set_ylabel('Time (seconds)')
        ax.set_xlabel('Framework')
        ax.legend(title='Agent Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Performance Summary
        ax = axes[1, 1]
        summary_data = []
        for framework in creation_time_df['framework'].unique():
            fw_data = creation_time_df[creation_time_df['framework'] == framework]
            avg_time = fw_data['value'].mean()
            summary_data.append({'Framework': framework, 'Avg Creation Time': avg_time})
        
        summary_df = pd.DataFrame(summary_data)
        sns.barplot(data=summary_df, x='Framework', y='Avg Creation Time', ax=ax)
        ax.set_title('Average Creation Time')
        ax.set_ylabel('Time (seconds)')
        
        # Add performance annotations
        for bar in ax.patches:
            if hasattr(bar, 'get_height') and hasattr(bar, 'get_x') and hasattr(bar, 'get_width'):
                height = bar.get_height()  # type: ignore
                x = bar.get_x()  # type: ignore
                width = bar.get_width()  # type: ignore
                ax.text(x + width/2., height + 0.001,
                       f'{height:.3f}s', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'startup_performance.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'startup_performance.pdf', bbox_inches='tight')
        print("📊 Startup performance chart saved")
        
    def create_conversation_performance_chart(self) -> None:
        """Create conversation performance comparison chart."""
        conv_df = self.df[self.df['category'] == 'conversation']
        
        if conv_df.empty:
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('💬 Conversation Performance Comparison', fontsize=16, fontweight='bold')
        
        # Average time per message
        avg_time_df = conv_df[conv_df['metric'] == 'avg_time_per_message']
        if not avg_time_df.empty:
            ax = axes[0, 0]
            sns.barplot(data=avg_time_df, x='framework', y='value', hue='test_name', ax=ax)
            ax.set_title('Average Response Time by Complexity')
            ax.set_ylabel('Time per Message (seconds)')
            ax.set_xlabel('')
            
        # Total conversation time
        total_time_df = conv_df[conv_df['metric'] == 'total_time']
        if not total_time_df.empty:
            ax = axes[0, 1]
            sns.barplot(data=total_time_df, x='framework', y='value', hue='test_name', ax=ax)
            ax.set_title('Total Conversation Time')
            ax.set_ylabel('Total Time (seconds)')
            ax.set_xlabel('')
            
        # Performance by complexity
        ax = axes[1, 0]
        if not avg_time_df.empty:
            complexity_pivot = avg_time_df.pivot_table(
                index='framework', columns='test_name', values='value', aggfunc='mean'
            )
            complexity_pivot.plot(kind='line', marker='o', ax=ax)
            ax.set_title('Response Time Scaling by Complexity')
            ax.set_ylabel('Time per Message (seconds)')
            ax.set_xlabel('Framework')
            ax.legend(title='Complexity', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Efficiency score (lower is better)
        ax = axes[1, 1]
        efficiency_data = []
        for framework in avg_time_df['framework'].unique():
            fw_data = avg_time_df[avg_time_df['framework'] == framework]
            efficiency = fw_data['value'].mean()  # Average response time
            efficiency_data.append({'framework': framework, 'Efficiency Score': efficiency})
        
        efficiency_df = pd.DataFrame(efficiency_data)
        bars = sns.barplot(data=efficiency_df, x='framework', y='Efficiency Score', ax=ax)
        ax.set_title('Overall Efficiency Score (Lower = Better)')
        ax.set_ylabel('Average Response Time (seconds)')
        
        # Color bars based on performance (green = best, red = worst)
        values = efficiency_df['Efficiency Score'].values
        if len(values) > 0:
            values_list = [float(x) for x in values]
            min_val, max_val = min(values_list), max(values_list)
            for bar, val in zip(bars.patches, values_list):
                normalized = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
                # Use a safe colormap - create color from RGB
                if normalized < 0.5:
                    # Green for better performance
                    color = (0.0, 0.8, 0.0, 1.0)
                else:
                    # Red for worse performance  
                    color = (0.8, 0.0, 0.0, 1.0)
                bar.set_color(color)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'conversation_performance.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'conversation_performance.pdf', bbox_inches='tight')
        print("📊 Conversation performance chart saved")
        
    def create_concurrency_performance_chart(self) -> None:
        """Create concurrency performance comparison chart."""
        conc_df = self.df[self.df['category'] == 'concurrency']
        
        if conc_df.empty:
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('⚡ Concurrency Performance Comparison', fontsize=16, fontweight='bold')
        
        # Throughput comparison
        throughput_df = conc_df[conc_df['metric'] == 'throughput']
        if not throughput_df.empty:
            ax = axes[0, 0]
            sns.barplot(data=throughput_df, x='framework', y='value', hue='test_name', ax=ax)
            ax.set_title('Message Throughput')
            ax.set_ylabel('Messages per Second')
            ax.set_xlabel('')
            
        # Memory usage under load
        memory_df = conc_df[conc_df['metric'] == 'memory_usage']
        if not memory_df.empty:
            ax = axes[0, 1]
            sns.barplot(data=memory_df, x='framework', y='value', hue='test_name', ax=ax)
            ax.set_title('Memory Usage Under Load')
            ax.set_ylabel('Memory Delta (MB)')
            ax.set_xlabel('')
            
        # Scalability analysis
        ax = axes[1, 0]
        if not throughput_df.empty:
            scalability_pivot = throughput_df.pivot_table(
                index='framework', columns='test_name', values='value', aggfunc='mean'
            )
            scalability_pivot.plot(kind='line', marker='s', ax=ax, linewidth=2, markersize=8)
            ax.set_title('Scalability Pattern')
            ax.set_ylabel('Throughput (messages/sec)')
            ax.set_xlabel('Framework')
            ax.legend(title='Test Configuration', bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            
        # Performance efficiency (throughput vs memory)
        ax = axes[1, 1]
        if not throughput_df.empty and not memory_df.empty:
            efficiency_data = []
            for framework in throughput_df['framework'].unique():
                tp_data = throughput_df[throughput_df['framework'] == framework]['value'].max()
                mem_data = memory_df[memory_df['framework'] == framework]['value'].mean()
                efficiency = tp_data / max(mem_data, 1)  # Throughput per MB
                efficiency_data.append({
                    'Framework': framework, 
                    'Efficiency': efficiency,
                    'Throughput': tp_data,
                    'Memory': mem_data
                })
            
            if efficiency_data:
                eff_df = pd.DataFrame(efficiency_data)
                bars = sns.barplot(data=eff_df, x='Framework', y='Efficiency', ax=ax)
                ax.set_title('Performance Efficiency\n(Throughput per MB)')
                ax.set_ylabel('Messages/sec per MB')
                
                # Annotate with actual values
                for bar in bars.patches:
                    if hasattr(bar, 'get_height') and hasattr(bar, 'get_x') and hasattr(bar, 'get_width'):
                        height = bar.get_height()  # type: ignore
                        x = bar.get_x()  # type: ignore
                        width = bar.get_width()  # type: ignore
                        ax.text(x + width/2., height + 0.1,
                               f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'concurrency_performance.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'concurrency_performance.pdf', bbox_inches='tight')
        print("📊 Concurrency performance chart saved")
        
    def create_overall_comparison_chart(self) -> None:
        """Create comprehensive comparison chart."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('🏆 Niflheim-X vs Competition: Complete Performance Analysis', 
                    fontsize=18, fontweight='bold')
        
        # Overall performance radar chart would go here
        # For now, create summary comparisons
        
        frameworks = self.df['framework'].unique()
        
        # 1. Startup Speed Summary
        ax = axes[0, 0]
        startup_summary = []
        startup_df = self.df[(self.df['category'] == 'startup') & (self.df['metric'] == 'creation_time')]
        for fw in frameworks:
            fw_data = startup_df[startup_df['framework'] == fw]
            avg_startup = fw_data['value'].mean() if not fw_data.empty else 0
            startup_summary.append({'Framework': fw, 'Avg Startup Time': avg_startup})
        
        if startup_summary:
            startup_summary_df = pd.DataFrame(startup_summary)
            bars = sns.barplot(data=startup_summary_df, x='Framework', y='Avg Startup Time', ax=ax)
            ax.set_title('⚡ Startup Speed\n(Lower = Better)', fontweight='bold')
            ax.set_ylabel('Average Time (seconds)')
            
            # Color the best performer
            min_idx = startup_summary_df['Avg Startup Time'].idxmin()
            for i, bar in enumerate(bars.patches):
                if i == min_idx:
                    bar.set_color('#2E8B57')  # Green for winner
                    if hasattr(bar, 'get_height') and hasattr(bar, 'get_x') and hasattr(bar, 'get_width'):
                        height = bar.get_height()  # type: ignore
                        x = bar.get_x()  # type: ignore
                        width = bar.get_width()  # type: ignore
                        ax.text(x + width/2., height + 0.001,
                               '🏆 FASTEST', ha='center', va='bottom', fontweight='bold', color='green')
        
        # 2. Response Speed Summary
        ax = axes[0, 1]
        response_summary = []
        response_df = self.df[(self.df['category'] == 'conversation') & (self.df['metric'] == 'avg_time_per_message')]
        for fw in frameworks:
            fw_data = response_df[response_df['framework'] == fw]
            avg_response = fw_data['value'].mean() if not fw_data.empty else 0
            response_summary.append({'Framework': fw, 'Avg Response Time': avg_response})
        
        if response_summary:
            response_summary_df = pd.DataFrame(response_summary)
            bars = sns.barplot(data=response_summary_df, x='Framework', y='Avg Response Time', ax=ax)
            ax.set_title('💬 Response Speed\n(Lower = Better)', fontweight='bold')
            ax.set_ylabel('Average Time per Message (seconds)')
            
            # Color the best performer
            min_idx = response_summary_df['Avg Response Time'].idxmin()
            for i, bar in enumerate(bars.patches):
                if i == min_idx:
                    bar.set_color('#2E8B57')  # Green for winner
                    if hasattr(bar, 'get_height') and hasattr(bar, 'get_x') and hasattr(bar, 'get_width'):
                        height = bar.get_height()  # type: ignore
                        x = bar.get_x()  # type: ignore
                        width = bar.get_width()  # type: ignore
                        ax.text(x + width/2., height + 0.01,
                               '🏆 FASTEST', ha='center', va='bottom', fontweight='bold', color='green')
        
        # 3. Throughput Summary
        ax = axes[1, 0]
        throughput_summary = []
        throughput_df = self.df[(self.df['category'] == 'concurrency') & (self.df['metric'] == 'throughput')]
        for fw in frameworks:
            fw_data = throughput_df[throughput_df['framework'] == fw]
            max_throughput = fw_data['value'].max() if not fw_data.empty else 0
            throughput_summary.append({'Framework': fw, 'Peak Throughput': max_throughput})
        
        if throughput_summary:
            throughput_summary_df = pd.DataFrame(throughput_summary)
            bars = sns.barplot(data=throughput_summary_df, x='Framework', y='Peak Throughput', ax=ax)
            ax.set_title('⚡ Peak Throughput\n(Higher = Better)', fontweight='bold')
            ax.set_ylabel('Messages per Second')
            
            # Color the best performer
            max_idx = throughput_summary_df['Peak Throughput'].idxmax()
            for i, bar in enumerate(bars.patches):
                if i == max_idx:
                    bar.set_color('#2E8B57')  # Green for winner
                    if hasattr(bar, 'get_height') and hasattr(bar, 'get_x') and hasattr(bar, 'get_width'):
                        height = bar.get_height()  # type: ignore
                        x = bar.get_x()  # type: ignore
                        width = bar.get_width()  # type: ignore
                        ax.text(x + width/2., height + 0.1,
                               '🏆 HIGHEST', ha='center', va='bottom', fontweight='bold', color='green')
        
        # 4. Overall Winner Analysis
        ax = axes[1, 1]
        ax.text(0.5, 0.8, '🏆 PERFORMANCE CHAMPION', ha='center', va='center', 
                fontsize=16, fontweight='bold', transform=ax.transAxes)
        
        # Calculate overall scores
        scores = {}
        for fw in frameworks:
            score = 0
            
            # Startup score (lower is better, so invert)
            startup_data = startup_df[startup_df['framework'] == fw]
            if not startup_data.empty:
                startup_avg = startup_data['value'].mean()
                startup_score = 1 / (startup_avg + 0.001)  # Invert and avoid division by zero
                score += startup_score * 30  # 30% weight
            
            # Response score (lower is better, so invert)
            response_data = response_df[response_df['framework'] == fw]
            if not response_data.empty:
                response_avg = response_data['value'].mean()
                response_score = 1 / (response_avg + 0.001)
                score += response_score * 40  # 40% weight
            
            # Throughput score (higher is better)
            throughput_data = throughput_df[throughput_df['framework'] == fw]
            if not throughput_data.empty:
                throughput_max = throughput_data['value'].max()
                score += throughput_max * 30  # 30% weight
            
            scores[fw] = score
        
        if scores:
            winner = max(scores.keys(), key=lambda k: scores[k])
            ax.text(0.5, 0.5, f'🥇 {winner.upper()}', ha='center', va='center',
                   fontsize=20, fontweight='bold', color='green', transform=ax.transAxes)
            
            ax.text(0.5, 0.3, f'Overall Performance Score: {scores[winner]:.1f}',
                   ha='center', va='center', fontsize=12, transform=ax.transAxes)
            
            # Show all scores
            score_text = "\n".join([f"{fw}: {score:.1f}" for fw, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)])
            ax.text(0.5, 0.1, score_text, ha='center', va='center',
                   fontsize=10, transform=ax.transAxes)
        
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'overall_comparison.png', dpi=300, bbox_inches='tight')
        plt.savefig(self.output_dir / 'overall_comparison.pdf', bbox_inches='tight')
        print("📊 Overall comparison chart saved")
        
    def generate_all_charts(self) -> None:
        """Generate all benchmark visualization charts."""
        print("🎨 Generating benchmark visualization charts...")
        
        self.create_startup_performance_chart()
        self.create_conversation_performance_chart()
        self.create_concurrency_performance_chart()
        self.create_overall_comparison_chart()
        
        print(f"✅ All charts generated in {self.output_dir}")
        print(f"📊 Charts available in PNG and PDF formats")


def main():
    """Main visualization function."""
    parser = argparse.ArgumentParser(description="Generate benchmark visualization charts")
    parser.add_argument("--results-file", required=True, help="JSON results file from benchmark run")
    parser.add_argument("--output-dir", default="./benchmark_charts", help="Output directory for charts")
    
    args = parser.parse_args()
    
    visualizer = BenchmarkVisualizer(args.results_file, args.output_dir)
    visualizer.generate_all_charts()


if __name__ == "__main__":
    main()