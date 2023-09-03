<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();

const address = router.currentRoute.value.params.address;
</script>

<template>
  <section class="miner-content">
    <div class="miner-content__text">
      <h2>
        {{ address }}
      </h2>
      <p>
        Miner violations and risk score history
      </p>
    </div>
  </section>
</template>

<style lang="scss">
@import "@/assets/breakpoints.scss";

.miner-content {
  padding: 4rem 0;
  word-break: break-all;
}

@media (min-width: $breakpoint-tablet) {
  .miner-content {
    padding: 3rem 0;
  }
}

@media (min-width: $breakpoint-desktop) {
  .miner-content {
    padding: 7.5rem 0;
    word-break: break-all;
  }
}
</style>
