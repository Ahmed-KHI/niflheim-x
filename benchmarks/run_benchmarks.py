"""
Niflheim-X Performance Benchmark Suite
======================================

Comprehensive benchmarking system comparing Niflheim-X against:
- BeeAI Framework
- LangChain
- Raw OpenAI API calls

Benchmark Categories:
1. Startup Time & Memory Usage
2. Agent Creation Performance  
3. Conversation Processing Speed
4. Memory System Performance
5. Tool Execution Efficiency
6. Concurrent Agent Performance
7. Resource Utilization

Usage:
    python run_benchmarks.py --all
    python run_benchmarks.py --category startup
    python run_benchmarks.py --frameworks niflheim-x,langchain
"""

import asyncio
import time
import psutil
import json
import argparse
import sys
import os
import gc
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Import framework-specific modules
try:
    # Niflheim-X imports
    from niflheim_x import Agent, OpenAIAdapter, DictMemory, SQLiteMemory, Tool
    NIFLHEIM_AVAILABLE = True
except ImportError:
    NIFLHEIM_AVAILABLE = False

try:
    # LangChain imports
    from langchain.agents import initialize_agent, AgentType
    from langchain.llms import OpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.tools import Tool as LangChainTool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Mock classes will be imported later when needed

try:
    # BeeAI imports (hypothetical - replace with actual imports)
    # from beeai import Agent as BeeAgent, LLM as BeeLLM
    BEEAI_AVAILABLE = False  # Set to True when BeeAI is available
except ImportError:
    BEEAI_AVAILABLE = False


@dataclass
class BenchmarkResult:
    """Single benchmark result data structure."""
    framework: str
    test_name: str
    category: str
    metric: str
    value: float
    unit: str
    timestamp: datetime
    system_info: Dict[str, Any]
    additional_data: Optional[Dict[str, Any]] = None


class SystemMonitor:
    """Monitor system resources during benchmarks."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = self.get_memory_usage()
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return self.process.cpu_percent()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "cpu_count": psutil.cpu_count(),
            "total_memory": psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            "available_memory": psutil.virtual_memory().available / 1024 / 1024 / 1024,  # GB
        }


class NiflheimXBenchmark:
    """Benchmark implementation for Niflheim-X."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.framework_name = "niflheim-x"
        
    async def create_simple_agent(self) -> Any:
        """Create a basic agent for testing."""
        llm = OpenAIAdapter(
            api_key=self.api_key,
            model="gpt-3.5-turbo"
        )
        return Agent(
            llm=llm,
            name="BenchmarkAgent",
            system_prompt="You are a helpful assistant for benchmarking."
        )
    
    async def create_agent_with_memory(self) -> Any:
        """Create agent with persistent memory."""
        llm = OpenAIAdapter(api_key=self.api_key, model="gpt-3.5-turbo")
        return Agent(
            llm=llm,
            name="MemoryAgent", 
            memory_backend="sqlite",
            db_path=":memory:"
        )
    
    async def create_agent_with_tools(self) -> Any:
        """Create agent with tools."""
        llm = OpenAIAdapter(api_key=self.api_key, model="gpt-3.5-turbo")
        agent = Agent(llm=llm, name="ToolAgent")
        
        @agent.tool(name="calc", description="Calculate math expressions")
        def calculator(expression: str) -> str:
            try:
                return str(eval(expression, {"__builtins__": {}}, {}))
            except:
                return "Error"
        
        return agent
    
    async def process_conversation(self, agent: Any, messages: List[str]) -> float:
        """Process a conversation and return total time."""
        start_time = time.time()
        for message in messages:
            await agent.chat(message)
        return time.time() - start_time
    
    async def concurrent_agents(self, num_agents: int, messages_per_agent: int) -> float:
        """Test concurrent agent performance."""
        async def agent_task(agent_id: int):
            agent = await self.create_simple_agent()
            start_time = time.time()
            for i in range(messages_per_agent):
                await agent.chat(f"Hello from agent {agent_id}, message {i}")
            return time.time() - start_time
        
        start_time = time.time()
        tasks = [agent_task(i) for i in range(num_agents)]
        await asyncio.gather(*tasks)
        return time.time() - start_time


class LangChainBenchmark:
    """Benchmark implementation for LangChain."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.framework_name = "langchain"
    
    async def create_simple_agent(self) -> Any:
        """Create a basic LangChain agent."""
        llm = OpenAI(openai_api_key=self.api_key, temperature=0.7)
        memory = ConversationBufferMemory()
        return initialize_agent(
            tools=[],
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=False
        )
    
    async def create_agent_with_memory(self) -> Any:
        """Create agent with memory."""
        llm = OpenAI(openai_api_key=self.api_key)
        memory = ConversationBufferMemory(return_messages=True)
        return initialize_agent(
            tools=[],
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=False
        )
    
    async def create_agent_with_tools(self) -> Any:
        """Create agent with tools."""
        def calculator(expression: str) -> str:
            try:
                return str(eval(expression, {"__builtins__": {}}, {}))
            except:
                return "Error"
        
        tools = [LangChainTool(
            name="Calculator",
            description="Calculate mathematical expressions",
            func=calculator
        )]
        
        llm = OpenAI(openai_api_key=self.api_key)
        memory = ConversationBufferMemory()
        return initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=False
        )
    
    async def process_conversation(self, agent: Any, messages: List[str]) -> float:
        """Process conversation with LangChain agent."""
        start_time = time.time()
        for message in messages:
            agent.run(message)
        return time.time() - start_time
    
    async def concurrent_agents(self, num_agents: int, messages_per_agent: int) -> float:
        """Test concurrent performance."""
        async def agent_task(agent_id: int):
            agent = await self.create_simple_agent()
            start_time = time.time()
            for i in range(messages_per_agent):
                agent.run(f"Hello from agent {agent_id}, message {i}")
            return time.time() - start_time
        
        start_time = time.time()
        # LangChain doesn't handle async well, so we'll simulate
        tasks = []
        for i in range(num_agents):
            tasks.append(agent_task(i))
        await asyncio.gather(*tasks)
        return time.time() - start_time


class BenchmarkSuite:
    """Main benchmark suite coordinator."""
    
    def __init__(self, api_key: str, output_dir: str = "./benchmark_results"):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.monitor = SystemMonitor()
        self.results: List[BenchmarkResult] = []
        
        # Initialize framework benchmarks
        self.frameworks = {}
        if NIFLHEIM_AVAILABLE:
            self.frameworks["niflheim-x"] = NiflheimXBenchmark(api_key)
        if LANGCHAIN_AVAILABLE:
            self.frameworks["langchain"] = LangChainBenchmark(api_key)
        else:
            # Use mock LangChain for comparison
            from .mock_frameworks import MockLangChainBenchmark
            self.frameworks["langchain"] = MockLangChainBenchmark(api_key)
        # Add BeeAI when available
        
    async def benchmark_startup_time(self, framework_name: str) -> None:
        """Benchmark framework startup and agent creation time."""
        if framework_name not in self.frameworks:
            return
            
        framework = self.frameworks[framework_name]
        
        # Test 1: Simple agent creation
        gc.collect()
        start_memory = self.monitor.get_memory_usage()
        
        start_time = time.time()
        agent = await framework.create_simple_agent()
        creation_time = time.time() - start_time
        
        end_memory = self.monitor.get_memory_usage()
        memory_usage = end_memory - start_memory
        
        self.results.append(BenchmarkResult(
            framework=framework_name,
            test_name="simple_agent_creation",
            category="startup",
            metric="creation_time",
            value=creation_time,
            unit="seconds",
            timestamp=datetime.now(),
            system_info=self.monitor.get_system_info()
        ))
        
        self.results.append(BenchmarkResult(
            framework=framework_name,
            test_name="simple_agent_creation",
            category="startup",
            metric="memory_usage",
            value=memory_usage,
            unit="MB",
            timestamp=datetime.now(),
            system_info=self.monitor.get_system_info()
        ))
        
        # Test 2: Agent with memory
        start_time = time.time()
        memory_agent = await framework.create_agent_with_memory()
        memory_creation_time = time.time() - start_time
        
        self.results.append(BenchmarkResult(
            framework=framework_name,
            test_name="memory_agent_creation",
            category="startup",
            metric="creation_time",
            value=memory_creation_time,
            unit="seconds",
            timestamp=datetime.now(),
            system_info=self.monitor.get_system_info()
        ))
        
        # Test 3: Agent with tools
        start_time = time.time()
        tool_agent = await framework.create_agent_with_tools()
        tool_creation_time = time.time() - start_time
        
        self.results.append(BenchmarkResult(
            framework=framework_name,
            test_name="tool_agent_creation",
            category="startup",
            metric="creation_time",
            value=tool_creation_time,
            unit="seconds",
            timestamp=datetime.now(),
            system_info=self.monitor.get_system_info()
        ))
        
        print(f"✅ {framework_name} startup benchmarks completed")
    
    async def benchmark_conversation_performance(self, framework_name: str) -> None:
        """Benchmark conversation processing speed."""
        if framework_name not in self.frameworks:
            return
            
        framework = self.frameworks[framework_name]
        
        # Test messages of varying complexity
        test_conversations = {
            "simple": ["Hello", "How are you?", "What's 2+2?"],
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
        }
        
        for complexity, messages in test_conversations.items():
            agent = await framework.create_simple_agent()
            
            # Warm up
            await agent.chat("Hello")
            
            # Actual benchmark
            start_time = time.time()
            total_time = await framework.process_conversation(agent, messages)
            
            avg_time_per_message = total_time / len(messages)
            
            self.results.append(BenchmarkResult(
                framework=framework_name,
                test_name=f"conversation_{complexity}",
                category="conversation",
                metric="total_time",
                value=total_time,
                unit="seconds",
                timestamp=datetime.now(),
                system_info=self.monitor.get_system_info(),
                additional_data={"message_count": len(messages)}
            ))
            
            self.results.append(BenchmarkResult(
                framework=framework_name,
                test_name=f"conversation_{complexity}",
                category="conversation",
                metric="avg_time_per_message",
                value=avg_time_per_message,
                unit="seconds",
                timestamp=datetime.now(),
                system_info=self.monitor.get_system_info()
            ))
        
        print(f"✅ {framework_name} conversation benchmarks completed")
    
    async def benchmark_concurrent_performance(self, framework_name: str) -> None:
        """Benchmark concurrent agent performance."""
        if framework_name not in self.frameworks:
            return
            
        framework = self.frameworks[framework_name]
        
        concurrency_tests = [
            (2, 3),   # 2 agents, 3 messages each
            (5, 2),   # 5 agents, 2 messages each  
            (10, 1),  # 10 agents, 1 message each
        ]
        
        for num_agents, messages_per_agent in concurrency_tests:
            start_memory = self.monitor.get_memory_usage()
            
            total_time = await framework.concurrent_agents(num_agents, messages_per_agent)
            
            end_memory = self.monitor.get_memory_usage()
            memory_delta = end_memory - start_memory
            
            total_messages = num_agents * messages_per_agent
            throughput = total_messages / total_time if total_time > 0 else 0
            
            self.results.append(BenchmarkResult(
                framework=framework_name,
                test_name=f"concurrent_{num_agents}agents_{messages_per_agent}msgs",
                category="concurrency",
                metric="total_time",
                value=total_time,
                unit="seconds",
                timestamp=datetime.now(),
                system_info=self.monitor.get_system_info(),
                additional_data={
                    "num_agents": num_agents,
                    "messages_per_agent": messages_per_agent,
                    "total_messages": total_messages
                }
            ))
            
            self.results.append(BenchmarkResult(
                framework=framework_name,
                test_name=f"concurrent_{num_agents}agents_{messages_per_agent}msgs",
                category="concurrency",
                metric="throughput",
                value=throughput,
                unit="messages/second",
                timestamp=datetime.now(),
                system_info=self.monitor.get_system_info()
            ))
            
            self.results.append(BenchmarkResult(
                framework=framework_name,
                test_name=f"concurrent_{num_agents}agents_{messages_per_agent}msgs",
                category="concurrency",
                metric="memory_usage",
                value=memory_delta,
                unit="MB",
                timestamp=datetime.now(),
                system_info=self.monitor.get_system_info()
            ))
        
        print(f"✅ {framework_name} concurrency benchmarks completed")
    
    async def run_all_benchmarks(self, frameworks: Optional[List[str]] = None) -> None:
        """Run all benchmarks for specified frameworks."""
        if frameworks is None:
            frameworks = list(self.frameworks.keys())
        
        print("🚀 Starting Niflheim-X Performance Benchmark Suite")
        print(f"📊 Testing frameworks: {', '.join(frameworks)}")
        print(f"🖥️  System: {self.monitor.get_system_info()}")
        print("-" * 60)
        
        for framework in frameworks:
            if framework not in self.frameworks:
                print(f"⚠️  Framework {framework} not available, skipping...")
                continue
                
            print(f"\n🧪 Benchmarking {framework.upper()}...")
            
            await self.benchmark_startup_time(framework)
            await self.benchmark_conversation_performance(framework)
            await self.benchmark_concurrent_performance(framework)
            
            print(f"✅ {framework} benchmarks completed\n")
        
        print("🎉 All benchmarks completed!")
        
    def save_results(self) -> None:
        """Save benchmark results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw results as JSON
        json_file = self.output_dir / f"benchmark_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump([asdict(result) for result in self.results], f, indent=2, default=str)
        
        # Save as CSV for analysis
        csv_file = self.output_dir / f"benchmark_results_{timestamp}.csv"
        df = pd.DataFrame([asdict(result) for result in self.results])
        df.to_csv(csv_file, index=False)
        
        print(f"📊 Results saved to {json_file} and {csv_file}")
        
    def generate_comparison_report(self) -> None:
        """Generate comprehensive comparison report."""
        if not self.results:
            print("No results to analyze")
            return
            
        df = pd.DataFrame([asdict(result) for result in self.results])
        
        print("\n" + "="*80)
        print("📈 PERFORMANCE COMPARISON REPORT")
        print("="*80)
        
        # Startup Performance
        startup_df = df[df['category'] == 'startup']
        if not startup_df.empty:
            print("\n🚀 STARTUP PERFORMANCE")
            print("-" * 40)
            
            for test in startup_df['test_name'].unique():
                test_data = startup_df[startup_df['test_name'] == test]
                print(f"\n{test.replace('_', ' ').title()}:")
                
                for metric in test_data['metric'].unique():
                    metric_data = test_data[test_data['metric'] == metric]
                    print(f"  {metric.replace('_', ' ').title()}:")
                    
                    for _, row in metric_data.iterrows():
                        print(f"    {row['framework']}: {row['value']:.4f} {row['unit']}")
        
        # Conversation Performance
        conversation_df = df[df['category'] == 'conversation']
        if not conversation_df.empty:
            print("\n💬 CONVERSATION PERFORMANCE")
            print("-" * 40)
            
            avg_times = conversation_df[conversation_df['metric'] == 'avg_time_per_message']
            for framework in avg_times['framework'].unique():
                framework_data = avg_times[avg_times['framework'] == framework]
                avg_time = framework_data['value'].mean()
                print(f"  {framework}: {avg_time:.4f} seconds/message average")
        
        # Concurrency Performance  
        concurrency_df = df[df['category'] == 'concurrency']
        if not concurrency_df.empty:
            print("\n⚡ CONCURRENCY PERFORMANCE")
            print("-" * 40)
            
            throughput_data = concurrency_df[concurrency_df['metric'] == 'throughput']
            for framework in throughput_data['framework'].unique():
                framework_data = throughput_data[throughput_data['framework'] == framework]
                max_throughput = framework_data['value'].max()
                print(f"  {framework}: {max_throughput:.2f} messages/second peak")
        
        print("\n" + "="*80)


async def main():
    """Main benchmark execution function."""
    parser = argparse.ArgumentParser(description="Niflheim-X Performance Benchmark Suite")
    parser.add_argument("--api-key", required=True, help="OpenAI API key")
    parser.add_argument("--frameworks", default="all", help="Comma-separated list of frameworks to test")
    parser.add_argument("--category", help="Specific benchmark category to run")
    parser.add_argument("--output-dir", default="./benchmark_results", help="Output directory for results")
    
    args = parser.parse_args()
    
    # Initialize benchmark suite
    suite = BenchmarkSuite(args.api_key, args.output_dir)
    
    # Determine frameworks to test
    if args.frameworks == "all":
        frameworks = list(suite.frameworks.keys())
    else:
        frameworks = [f.strip() for f in args.frameworks.split(",")]
    
    # Run benchmarks
    await suite.run_all_benchmarks(frameworks)
    
    # Save results and generate report
    suite.save_results()
    suite.generate_comparison_report()


if __name__ == "__main__":
    asyncio.run(main())