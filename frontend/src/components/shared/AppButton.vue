<script setup>
defineProps({
  type: {
    type: String,
    default: 'primary',
  },
});

</script>

<template>
  <button
    class="app-button"
    :class="`app-button--${type}`"
  >
    <slot></slot>
  </button>
</template>

<style lang="scss">
@import "@/assets/colors.scss";

.app-button {
  display: flex;
  padding: 1rem 1.75rem;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(16, 24, 40, 0.05);
  font-size: 1.125rem;
  font-style: normal;
  font-weight: 600;
  line-height: 1.75rem;
  cursor: pointer;

  &--primary {
    background: $primary-600;
    border: 1px solid $primary-600;
    color: $base-white;

    &:hover,
    &:focus {
      background: $primary-700;
      border: 1px solid $primary-700;
    }
  }

  &--secondary {
    background: $base-white;
    border: 1px solid $gray-300;
    color: $gray-700;

    &:hover,
    &:focus {
      background: $gray-50;
      border: 1px solid $gray-300;
      color: $gray-800;
    }
  }
}
</style>
