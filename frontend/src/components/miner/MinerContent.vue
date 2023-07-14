<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();

const address = router.currentRoute.value.params.address;
</script>

<template>
  <section class="miner-content">
    <div class="miner-content__text">
      <h1>
        {{ address }}
      </h1>
      <h2>
        Miner violations and risk score history
      </h2>
    </div>
    <div class="miner-content__graphics" />
  </section>
</template>

<style lang="scss">
.miner-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2.5rem;
  padding: 7.5rem 0;

  .miner-content__text {
    h1 {
      font-size: 1.5rem;
      font-weight: 600;
      line-height: 120%;
      color: var(--color-heading);
    }
    h2 {
      font-size: 1rem;
      font-weight: 500;
      color: var(--color-heading-mute);
    }
  }

  .miner-content__graphics {
    background: rgba(38, 42, 45, 0);
  }
}
</style>
