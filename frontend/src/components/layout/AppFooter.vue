<script setup>
</script>

<template>
  <footer class="guardian-footer">
    <nav>
      <router-link to="/" class="guardian-footer__home-link">
        Guardian Labs
      </router-link>
      <div class="guardian-footer__central-navigation">
        <router-link to="/" class="guardian-footer__link">
          Network monitor
        </router-link>
        <router-link to="/" class="guardian-footer__link">
          About RPC
        </router-link>
        <router-link to="/" class="guardian-footer__link">
          Set up Router
        </router-link>
        <router-link to="/" class="guardian-footer__link">
          FAQ
        </router-link>
      </div>
      <a class="guardian-footer__copyright">© 2023 Guardian Labs</a>
    </nav>
  </footer>
</template>

<style lang="scss">
@import "@/assets/colors.scss";
@import "@/assets/breakpoints.scss";

.guardian-footer {
  padding-bottom: 2rem;
  padding-top: 2rem;
  background: $gray-50;
  .guardian-footer__central-navigation {
    display: none;
  }

  .guardian-footer__home-link {
    padding-left: 1rem;
    display: none;
  }

  .guardian-footer__link {
    color: $color-text;
    font-weight: 600;
    font-size: 1rem;
    text-decoration: none;
  }

  .guardian-footer__switch {
    display: none;
  }
  .guardian-footer__copyright {
    color: $gray-500;
    font-size: 16px;
    font-weight: 400;
    line-height: 24px;
    display: flex;
    justify-content: center;
    padding-right: 1rem;
    cursor: default;
  }
}

@media (min-width: $breakpoint-tablet) {
  .guardian-footer {
    padding-bottom: 2rem;
  }
}

@media (min-width: $breakpoint-desktop) {
  .guardian-footer {
    padding-bottom: 1rem;
    padding-top: 1rem;
    nav {
      display: flex;
      gap: 1.5rem;
      justify-content: space-between;
      align-items: center;
      align-content: center;
    }

    .guardian-footer__central-navigation {
        display: flex;
        gap: 1.5rem;
        justify-content: center;
    } 
    .guardian-footer__home-link {
      display: initial;
      color: $color-text-heading;
      text-decoration: none;
      font-size: 1.25rem;
      line-height: 1.5rem;
      font-weight: 600;
      width: 15rem;
    }

    .guardian-footer__switch {
      display: flex;
    }
  }
}
</style>
