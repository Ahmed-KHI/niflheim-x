import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/search',
    component: ComponentCreator('/search', '5de'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', 'de3'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '461'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '684'),
            routes: [
              {
                path: '/docs/core/agents',
                component: ComponentCreator('/docs/core/agents', '163'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/core/llms',
                component: ComponentCreator('/docs/core/llms', '5bc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/core/memory',
                component: ComponentCreator('/docs/core/memory', 'e6c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/core/tools',
                component: ComponentCreator('/docs/core/tools', 'f2d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/enterprise/observability',
                component: ComponentCreator('/docs/enterprise/observability', 'ee3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/examples/simple-qa-bot',
                component: ComponentCreator('/docs/examples/simple-qa-bot', '5d8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/getting-started',
                component: ComponentCreator('/docs/getting-started', '2a1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/guides/quick-start',
                component: ComponentCreator('/docs/guides/quick-start', 'de5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
