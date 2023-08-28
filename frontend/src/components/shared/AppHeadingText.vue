<template>
  <p class="app-heading-text">
    <slot></slot>
  </p>
</template>

<style lang="scss">
@import '@/assets/colors.scss';

.app-heading-text {
  color: $primary-700;
  font-size: 1rem;
  font-style: normal;
  font-weight: 600;
  line-height: 1.5rem;
  padding-bottom: 0.75rem;
}
</style>
