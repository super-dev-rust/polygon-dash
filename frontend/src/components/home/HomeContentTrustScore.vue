<script setup>
import HomeContentPieChart from '@/components/home/HomeContentPieChart.vue';
</script>

<template>
  <section class="home-content-trust-score">
    <div class="home-content-trust-score__legend-block">
      <h2>Trust Score Distribution</h2>
      <p>
        A concise graph showcasing the range of nodes,
        from the most trustworthy to the most suspicious.
      </p>
      <div>
        <ul>
          <li>
            <span class="home-content-trust-score__gradation home-content-trust-score__gradation--trusted">100-85</span>
            <span>Highly Trusted nodes</span>
          </li>
          <li>
            <span class="home-content-trust-score__gradation home-content-trust-score__gradation--suspicious">84−64</span>
            <span>Nodes with suspicious behaviour</span>
          </li>
          <li>
            <span class="home-content-trust-score__gradation home-content-trust-score__gradation--untrusted">63-0</span>
            <span>Untrusted nodes</span>
          </li>
        </ul>
      </div>
    </div>
    <HomeContentPieChart class="home-content-trust-score__chart-block"/>
  </section>
</template>

<style lang="scss">
@import "@/assets/colors.scss";
@import "@/assets/breakpoints.scss";

.home-content-trust-score {
  display: flex;
  flex-direction: column;
  padding: 3.5rem 0;
  gap: 2rem;
  align-items: center;

  .home-content-trust-score__legend-block {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;

    ul {
      padding: 0;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    li {
      list-style: none;
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      font-size: 16px;
      font-style: normal;
      font-weight: 400;
      line-height: 24px;
    }

    .home-content-trust-score__gradation {
      width: 4rem;

      &--trusted {
        color: #0C9253;
      }

      &--suspicious {
        color: #FFA450;
      }

      &--untrusted {
        color: #F04438;
      }
    }
  }

  .home-content-trust-score__chart-block {
    max-width: 300px;
  }
}

@media screen and (min-width: $breakpoint-desktop) {
  .home-content-trust-score {
    flex-direction: row;
    gap: 2rem;
    justify-content: space-between;
    padding: 6rem 0;

    .home-content-trust-score__legend-block {
      width: 50%;
    }
  }
}
</style>
