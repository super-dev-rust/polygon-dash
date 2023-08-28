<script setup>
import AppTabsBlockchains from '@/components/shared/AppTabsBlockchains.vue';
</script>

<template>
  <header class="guardian-header">
    <nav>
      <router-link to="/" class="guardian-header__home-link">
        Guardian Labs
      </router-link>
      <div class="guardian-header__central-navigation">
        <router-link to="/" class="guardian-header__link">
          About RPC
        </router-link>
        <router-link to="/" class="guardian-header__link">
          Set up Router
        </router-link>
        <router-link to="/" class="guardian-header__link">
          FAQ
        </router-link>
      </div>
      <AppTabsBlockchains class="guardian-header__switch"/>
    </nav>
  </header>
</template>

<style lang="scss">
@import "@/assets/colors.scss";
@import "@/assets/breakpoints.scss";

.guardian-header {
  padding-top: 2rem;
  padding-left: 1rem;
  padding-right: 1rem;

  .guardian-header__central-navigation {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
  }

  .guardian-header__home-link {
    display: none;
  }

  .guardian-header__link {
    color: $color-text;
    font-weight: 600;
    font-size: 1rem;
    text-decoration: none;
  }

  .guardian-header__switch {
    display: none;
  }
}

@media (min-width: $breakpoint-tablet) {
  .guardian-header {
    padding-top: 3.5rem;
  }
}

@media (min-width: $breakpoint-desktop) {
  .guardian-header {
    padding-top: 1rem;

    nav {
      display: flex;
      gap: 1.5rem;
      justify-content: space-between;
      align-items: center;
      align-content: center;
    }

    .guardian-header__home-link {
      display: initial;
      color: $color-text-heading;
      text-decoration: none;
      font-size: 1.25rem;
      line-height: 1.5rem;
      font-weight: 600;
      width: 15rem;
    }

    .guardian-header__switch {
      visibility: hidden;
      display: flex;
    }
  }
}
</style>
