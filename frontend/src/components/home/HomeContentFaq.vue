<script setup>

import AppHeadingText from '@/components/shared/AppHeadingText.vue';
import HomeContentFaqBlock from '@/components/home/HomeContentFaqBlock.vue';
</script>

<template>
  <section>
    <AppHeadingText>Got questions?</AppHeadingText>
    <h2>
      FAQs
    </h2>
    <p>
      Everything you need to know about the Router.
      Can’t find the answer you’re looking for?
      Please contact our team.
    </p>
    <div>
      <HomeContentFaqBlock>
        <template #header>
          Header
        </template>
        <span>Explanation about your rating methodology,
          sources of data, and validation processes.
          Explanation about your rating methodology,
          sources of data, and validation processes.
          Explanation about your rating methodology,
          sources of data, and validation processes.</span>
      </HomeContentFaqBlock>
    </div>
  </section>
</template>

<style scoped>

</style>
