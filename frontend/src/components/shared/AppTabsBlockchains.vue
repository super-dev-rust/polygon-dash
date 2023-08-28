<script setup>
import { ref } from 'vue';

import IconMatic from '@/assets/icons/icon-matic.svg';
import IconAda from '@/assets/icons/icon-ada.svg';
import IconMaticDisabled from '@/assets/icons/icon-matic-disabled.svg';
import IconAdaDisabled from '@/assets/icons/icon-ada-disabled.svg';

const blockchains = [
  {
    name: 'Polygon',
    icon: IconMatic,
    iconDisabled: IconMaticDisabled,
  },
  {
    name: 'Cardano',
    icon: IconAda,
    iconDisabled: IconAdaDisabled,
  },
];

const activeBlockchain = ref('Polygon');
const handleBlockchainSelection = (name) => {
  activeBlockchain.value = name;
};

</script>

<template>
<div class="app-tabs">
  <button
    v-for="chain in blockchains"
    class="app-tabs__button"
    :class="{ 'app-tabs__button--is-active': chain.name === activeBlockchain }"
    @click="handleBlockchainSelection(chain.name)"
  >
    <component :is="chain.name === activeBlockchain ? chain.icon : chain.iconDisabled" />
    {{ chain.name }}
  </button>
</div>
</template>

<style lang="scss">
@import "@/assets/colors.scss";

.app-tabs {
  background: $gray-50;
  display: flex;
  gap: 0.5rem;
  border: 1px solid $gray-200;
  padding: 0.25rem;
  border-radius: 0.5rem;
  max-width: 27.5rem;

  .app-tabs__button {
    border: none;
    border-radius: 6px;
    background: $gray-50;
    box-shadow: none;
    padding: 0.5rem 0.75rem;
    cursor: pointer;
    color: $gray-500;
    font-size: 0.875rem;
    font-style: normal;
    font-weight: 600;
    line-height: 1.25rem;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;

    &--is-active {
      background: $base-white;
      color: $gray-700;
      box-shadow: 0 1px 2px 0 rgba(16, 24, 40, 0.06), 0 1px 3px 0 rgba(16, 24, 40, 0.10);
    }
  }
}
</style>
