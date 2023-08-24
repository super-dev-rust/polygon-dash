<script setup>
import IconMinusCircle from "@/assets/icons/icon-minus-circle.svg";
import IconPlusCircle from "@/assets/icons/icon-plus-circle.svg";
import { ref } from 'vue';

const isExpanded = ref(false);
const toggle = () => {
  isExpanded.value = !isExpanded.value;
}
</script>

<template>
  <div class="home-content-faq-block">
    <div class="home-content-faq-block__text-section">
      <h3>
        <slot name="header"></slot>
      </h3>
      <p v-if="isExpanded">
        <slot></slot>
      </p>
    </div>
    <div class="home-content-faq-block__button-section">
      <component
        :is="isExpanded ? IconMinusCircle : IconPlusCircle"
        class="home-content-faq-block__button"
        @click="toggle"
      />
    </div>
  </div>
</template>

<style lang="scss">
@import "@/assets/colors.scss";
@import "@/assets/breakpoints.scss";

.home-content-faq-block {
  padding: 2rem;
  border-radius: 1rem;
  background: $gray-50;
  display: flex;
  gap: 1.5rem;
  justify-content: space-between;
  margin-bottom: 1rem;

  .home-content-faq-block__text-section {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  h3 {
    color: $gray-900;
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

  .home-content-faq-block__button {
    cursor: pointer;
  }
}


// @media screen and (min-width: $breakpoint-desktop) {
//   .home-content-faq-block {
//     padding: 2rem;
//     border-radius: 1rem;
//     background: $gray-50;
//     display: flex;
//     gap: 1.5rem;
//     justify-content: space-between;
//     flex-direction: row;
//     margin-top: 4rem;
//   }
// }
</style>
