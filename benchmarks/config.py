"""
Configuration for benchmark tests
"""

import os
from typing import Dict, Any

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# Test Configuration
BENCHMARK_CONFIG = {
    "test_categories": [
        "startup",
        "conversation", 
        "concurrency"
    ],
    
    "frameworks_to_test": [
        "niflheim-x",
        # "langchain",  # Enable when available
        # "beeai",      # Enable when available
    ],
    
    "conversation_test_messages": {
        "simple": [
            "Hello",
            "How are you?", 
            "What's 2+2?"
        ],
        "medium": [
            "Explain machine learning in one sentence",
            "What are the benefits of Python?",
            "How do you create a simple web server?"
        ],
        "complex": [
            "Explain the differences between supervised and unsupervised learning",
            "Write a Python function to calculate the Fibonacci sequence",
            "Compare and contrast different software architecture patterns"
        ]
    },
    
    "concurrency_tests": [
        {"num_agents": 2, "messages_per_agent": 3},
        {"num_agents": 5, "messages_per_agent": 2},
        {"num_agents": 10, "messages_per_agent": 1}
    ],
    
    "output_formats": ["json", "csv", "charts"],
    
    "chart_config": {
        "style": "seaborn",
        "dpi": 300,
        "formats": ["png", "pdf"],
        "color_scheme": {
            "niflheim-x": "#2E86AB",
            "langchain": "#A23B72",
            "beeai": "#F18F01", 
            "openai": "#84C7D0"
        }
    }
}

# Performance expectations (for validation)
EXPECTED_PERFORMANCE = {
    "niflheim-x": {
        "startup_time": {"max": 0.1, "target": 0.05},
        "response_time": {"max": 2.0, "target": 1.0},
        "memory_usage": {"max": 50, "target": 30},  # MB
        "throughput": {"min": 5, "target": 10}  # messages/sec
    },
    "langchain": {
        "startup_time": {"max": 0.5, "target": 0.2},
        "response_time": {"max": 3.0, "target": 1.5},
        "memory_usage": {"max": 80, "target": 50},
        "throughput": {"min": 2, "target": 5}
    }
}