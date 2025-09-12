import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: '⚡ Lightning Fast',
    Svg: require('@site/static/img/logo.svg').default,
    description: (
      <>
        50ms startup time vs LangChain's 2-5 seconds. Ultra-lightweight at 50KB 
        instead of 50MB. Production-ready performance that scales.
      </>
    ),
  },
  {
    title: '🛡️ Enterprise Ready',
    Svg: require('@site/static/img/logo.svg').default,
    description: (
      <>
        Only 3 core dependencies instead of 50+. Type-safe architecture with 
        comprehensive error handling. Built for production from day one.
      </>
    ),
  },
  {
    title: '🎯 Developer Friendly',
    Svg: require('@site/static/img/logo.svg').default,
    description: (
      <>
        Intuitive API design that gets you productive in minutes. Async-first 
        architecture with excellent debugging tools and documentation.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}