// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const {themes} = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Niflheim-X',
  tagline: 'Enterprise AI Agent Framework - Build production agents 10x faster',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://ahmed-khi.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/niflheim-x/',

  // GitHub pages deployment config
  organizationName: 'Ahmed-KHI', 
  projectName: 'niflheim-x',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/Ahmed-KHI/niflheim-x/tree/main/apps/docs-site/',
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/Ahmed-KHI/niflheim-x/tree/main/apps/docs-site/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/niflheim-x-social-card.jpg',
      navbar: {
        title: 'Niflheim-X',
        logo: {
          alt: 'Niflheim-X Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Docs',
          },
          {to: '/blog', label: 'Blog', position: 'left'},
          {
            href: 'https://github.com/Ahmed-KHI/niflheim-x',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Getting Started',
                to: '/docs/getting-started',
              },
              {
                label: 'Python Guide',
                to: '/docs/python/installation',
              },
              {
                label: 'TypeScript Guide',
                to: '/docs/typescript/installation',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Discord',
                href: 'https://discord.gg/niflheim-x',
              },
              {
                label: 'Twitter',
                href: 'https://twitter.com/niflheim_x',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/niflheim-x/niflheim-x',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Niflheim-X Team. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'typescript', 'bash'],
      },
      algolia: {
        // The application ID provided by Algolia
        appId: 'YOUR_APP_ID',
        // Public API key: it is safe to commit it
        apiKey: 'YOUR_SEARCH_API_KEY',
        indexName: 'niflheim-x',
        // Optional: see doc section below
        contextualSearch: true,
        // Optional: Replace parts of the item URLs from Algolia
        replaceSearchResultPathname: {
          from: '/docs/', // or as RegExp: /\/docs\//
          to: '/',
        },
        // Optional: path for search page that enabled by default (`false` to disable it)
        searchPagePath: 'search',
      },
    }),

  themes: ['@docusaurus/theme-live-codeblock'],
};

module.exports = config;