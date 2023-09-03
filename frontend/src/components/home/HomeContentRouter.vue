<script setup>
import AppTabsBlockchains from '@/components/shared/AppTabsBlockchains.vue';
import AppButton from '@/components/shared/AppButton.vue';
</script>

<template>
  <section class="home-content-router">
    <h1>
      Guardian Router: <br>
      A Web3 Trust Compass
    </h1>
    <AppTabsBlockchains class="home-content-router__chain-tabs" />
    <p class="home-content-router__text">
      Experience Web3 with unparalleled trust.
      Sidestep MEV, censorship, and reordering effortlessly through Guardian RPC service.
    </p>
    <div class="home-content-router__buttons">
      <router-link :to="{ name: 'home', hash: '#about' }" class="no-decoration">
        <AppButton type="secondary">
          How it works
        </AppButton>
      </router-link>
      <router-link :to="{ name: 'home', hash: '#steps' }" class="no-decoration">
        <AppButton>
          Set up Guardian Router
        </AppButton>
      </router-link>
    </div>
  </section>
</template>

<style lang="scss">
@import "@/assets/colors.scss";
@import "@/assets/breakpoints.scss";

.no-decoration {
  text-decoration: none;
}

.home-content-router {
  display: flex;
  margin-top: 1.5rem;
  gap: 1.5rem;
  flex-direction: column;
  text-align: center;
  align-items: center;


  .home-content-router__text {
    max-width: 42.5rem;
  }

  .home-content-router__chain-tabs {
    display: none;
    width: 100%;
  }

  .home-content-router__buttons {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 1.5rem;
    width: 100%;

    button {
      width: 100%;
    }
  }
}

@media screen and (min-width: $breakpoint-tablet) {
  .home-content-router {
    .home-content-router__buttons {
      display: flex;
      flex-direction: row;
      gap: 0.75rem;
      margin-top: 0.5rem;
      width: initial;
    }
  }
}

@media screen and (min-width: $breakpoint-desktop) {
  .home-content-router {
    margin-top: 6rem;

    .home-content-router__chain-tabs {
      display: none;
    }
  }
}
</style>
