<script setup>
import AppHeadingText from '@/components/shared/AppHeadingText.vue';
import HomeContentFaqBlock from '@/components/home/HomeContentFaqBlock.vue';


const FAQ_TEXT = [
  {
    header: "How do you ensure the accuracy of the node ratings?",
    text: "We ensure the accuracy of node ratings by deploying multiple crawlers to fetch data from miners' mempools and matching it with produced blocks. This process allows us to identify inconsistencies such as outliers (transactions inserted right before block creation), injections (transactions not in the mempool but in the block), and censorship (transactions in the mempool but not selected for the block).",
  },
  {
    header: "How often is the data updated on the dashboard?",
    text: "Given the rapid block times of the Polygon network, our dashboard keeps pace, updating with every new block.",
  },
  {
    header: "What happens if a highly-rated node starts displaying suspicious behavior?",
    text: "If a node that previously had a high trust score starts exhibiting suspicious behavior, its trust score will decrease significantly. Such nodes are then temporarily sidelined and are not used to route transactions for an extended period. However, we believe in second chances. The node will still be under our continuous monitoring, allowing it the opportunity to regain its trustworthiness. It's worth noting, though, that the journey back to becoming a 'trusted' node will require consistent positive behavior and will be closely watched over time.",
  }
];


</script>

<template>
  <section id="faq" class="home-content-faq">
    <AppHeadingText>Got questions?</AppHeadingText>
    <h2 class="home-content-faq__header">
      FAQs
    </h2>
    <p>
      Everything you need to know about the Router.
      Can’t find the answer you’re looking for?
      Please contact our team.
    </p>
    <div class="home-content-block_wrapper">
      <HomeContentFaqBlock v-for="faqBlock in FAQ_TEXT">
        <template #header>
          {{ faqBlock.header }}
        </template>
        <span>{{ faqBlock.text }}</span>
      </HomeContentFaqBlock>
    </div>
  </section>
</template>

<style lang="scss" scoped>
@import "@/assets/colors.scss";
@import "@/assets/breakpoints.scss";

.home-content-faq {
  padding: 3.5rem 0;
  .home-content-faq__header {
    padding-bottom: 1.25rem;
  }
  .home-content-block_wrapper {
    margin-top: 2rem;
  }
}


@media screen and (min-width: $breakpoint-desktop) {
  .home-content-faq {
    padding: 6rem 0;
    .home-content-block_wrapper{
      flex-direction: row;
      margin-top: 4rem;
    }
  }
}
</style>
