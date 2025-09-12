/**
 * Simple example demonstrating the TypeScript Agent
 */

import { Agent, SimpleDictMemory } from '../src/simple-agent.js';
import { ToolRegistry, createTool } from '../src/tools.js';
import { OpenAILLM } from '../src/llm/base.js';

// Create memory and tool registry
const memory = new SimpleDictMemory();
const toolRegistry = new ToolRegistry();

// Add a simple tool
const weatherTool = createTool({
  name: 'get_weather',
  description: 'Get weather for a location',
  function: (location: string) => {
    return `The weather in ${location} is sunny and 72°F`;
  },
  parameters: {
    type: 'object',
    properties: {
      location: {
        type: 'string',
        description: 'The location to get weather for'
      }
    },
    required: ['location']
  }
});

toolRegistry.registerTool(weatherTool);

// Create LLM instance (replace with your API key)
const llm = new OpenAILLM({
  model: 'gpt-3.5-turbo',
  apiKey: 'your-api-key-here' // Set your API key here
});

// Create agent
const agent = new Agent({
  name: 'WeatherBot',
  llm,
  memory,
  toolRegistry,
  systemPrompt: 'You are a helpful weather assistant.'
});

// Example usage
async function main() {
  try {
    console.log('🤖 TypeScript Agent Demo');
    console.log('========================');

    const response = await agent.chat('What is the weather like in San Francisco?');
    console.log('Agent:', response.content);

  } catch (error) {
    console.error('Error:', error);
  }
}

// Run the example
main();