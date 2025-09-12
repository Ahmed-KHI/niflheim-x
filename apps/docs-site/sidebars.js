/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    'intro',
    'getting-started',
    {
      type: 'category',
      label: 'Quick Start',
      items: [
        'guides/quick-start',
      ],
    },
    {
      type: 'category',
      label: 'Core Concepts',
      items: [
        'core/agents',
        'core/memory',
        'core/tools',
        'core/llms',
      ],
    },
    {
      type: 'category',
      label: 'Enterprise Features',
      items: [
        'enterprise/observability',
      ],
    },
    {
      type: 'category',
      label: 'Examples',
      items: [
        'examples/simple-qa-bot',
      ],
    },
  ],
};

module.exports = sidebars;