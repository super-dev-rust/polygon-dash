<script setup>
import AppHeadingText from '@/components/shared/AppHeadingText.vue';
import IconEye from '@/assets/icons/icon-eye.svg';
import IconLayers from '@/assets/icons/icon-layers.svg';
import IconPieChart from '@/assets/icons/icon-pie-chart.svg';

const CARDS = [
  {
    icon: IconEye,
    header: 'Real-Time Vigilance',
    text: 'As the Web3 landscape shifts, we stay watchful. ' +
      'Every moment, every change, captured to ensure you\'re always in the know.',
  },
  {
    icon: IconLayers,
    header: 'Transparent Trust Metrics',
    text: 'No more guesswork.' +
      ' Our criteria for node trustworthiness are clear-cut and openly accessible. Trust, but verify.',
  },
  {
    icon: IconPieChart,
    header: 'Data-Driven Insights',
    text: 'Stay ahead with our rigorously sourced data,' +
      ' giving you a clear view of node performance and trustworthiness.',
  },
];
</script>

<template>
  <section id="about" class="home-content-about">
    <AppHeadingText>About</AppHeadingText>
    <h2 class="home-content-about__header">
      Your Compass in the Web3 Odyssey
    </h2>
    <p>
      Within the expansive Web3 environment,
      identifying reliable nodes is crucial. We provide
      a straightforward tool to guide your decisions,
      ensuring you connect with the most trustworthy nodes.
    </p>
    <div class="home-content-about__card-block">
      <div v-for="card in CARDS" class="home-content-about__card">
        <div class="home-content-about__card-icon">
          <component :is="card.icon" />
        </div>
        <h3>{{ card.header }}</h3>
        <p>{{ card.text }}</p>
      </div>
    </div>
  </section>
</template>

<style lang="scss">
@import "@/assets/colors.scss";
@import "@/assets/breakpoints.scss";

.home-content-about {
  padding: 3.5rem 0;
  .home-content-about__header {
    padding-bottom: 1.25rem;
  }

  .home-content-about__card-block {
    margin-top: 2rem;
    padding-bottom: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .home-content-about__card {
    padding: 1.5rem;
    border-radius: 0.5rem;
    background: $gray-50;

    h3 {
      color: $gray-900;
      margin-top: 1.5rem;
      padding-bottom: 0.5rem;
      font-size: 1.125rem;
      font-style: normal;
      font-weight: 500;
      line-height: 1.75rem;
    }

    p {
      font-size: 1rem;
      font-style: normal;
      font-weight: 400;
      line-height: 1.5rem;
    }
  }

  .home-content-about__card-icon {
    padding: 0.75rem;
    width: 3rem;
    height: 3rem;
    border-radius: 0.625rem;
    background: $primary-700;
  }
}

@media screen and (min-width: $breakpoint-desktop) {
  .home-content-about {
    padding: 6rem 0;
    .home-content-about__card-block {
      flex-direction: row;
      margin-top: 4rem;
    }
  }
}
</style>
