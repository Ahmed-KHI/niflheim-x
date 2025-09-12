#!/usr/bin/env python3
"""
Quick benchmark runner for Niflheim-X performance testing
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from benchmarks.run_benchmarks import BenchmarkSuite
from benchmarks.visualize_results import BenchmarkVisualizer
from benchmarks.config import BENCHMARK_CONFIG, OPENAI_API_KEY

async def quick_benchmark():
    """Run a quick benchmark test."""
    
    # Check for API key
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your-api-key-here":
        print("❌ Error: Please set OPENAI_API_KEY environment variable")
        print("Usage: export OPENAI_API_KEY='your-key-here'")
        return
    
    print("🚀 Starting Niflheim-X Quick Benchmark")
    print("=" * 50)
    
    # Initialize benchmark suite
    suite = BenchmarkSuite(OPENAI_API_KEY, "./benchmark_results")
    
    # Run benchmarks for available frameworks
    available_frameworks = list(suite.frameworks.keys())
    print(f"📊 Available frameworks: {', '.join(available_frameworks)}")
    
    if not available_frameworks:
        print("❌ No frameworks available for testing")
        print("Please ensure Niflheim-X is properly installed")
        return
    
    # Run the benchmarks
    await suite.run_all_benchmarks(available_frameworks)
    
    # Save results
    suite.save_results()
    
    # Generate report
    suite.generate_comparison_report()
    
    # Find the latest results file
    results_dir = Path("./benchmark_results")
    if results_dir.exists():
        json_files = list(results_dir.glob("benchmark_results_*.json"))
        if json_files:
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            
            print(f"\n📊 Generating charts from {latest_file}")
            
            # Generate visualization charts
            visualizer = BenchmarkVisualizer(str(latest_file), "./benchmark_charts")
            visualizer.generate_all_charts()
            
            print("\n✅ Benchmark completed successfully!")
            print(f"📁 Results saved in: ./benchmark_results/")
            print(f"📊 Charts saved in: ./benchmark_charts/")
        else:
            print("⚠️  No results files found")
    else:
        print("⚠️  Results directory not found")

def main():
    """Main entry point."""
    try:
        asyncio.run(quick_benchmark())
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"❌ Error running benchmark: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()