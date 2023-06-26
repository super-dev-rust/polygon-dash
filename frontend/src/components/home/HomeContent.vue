<script setup>
</script>

<template>
  <section class="home-content">
    <div class="home-content__text">
      <h1>
        Let’s spot untrusted nodes
      </h1>
      <h2>
        Network integrity navigation. Non-compliant nodes highlight. Efficient decision-making aid
      </h2>
    </div>
    <div class="home-content__graphics" />
  </section>
</template>

<style lang="scss">
.home-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2.5rem;
  padding: 7.5rem 0;

  .home-content__text {
    h1 {
      font-size: 4rem;
      font-weight: 600;
      line-height: 120%;
      color: var(--color-heading);
    }
    h2 {
      font-size: 1.5rem;
      font-weight: 500;
      color: var(--color-heading-mute);
    }
  }

  .home-content__graphics {
    background: #262A2D;
  }
}
</style>
