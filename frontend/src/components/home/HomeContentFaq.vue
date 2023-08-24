<script setup>
import AppHeadingText from '@/components/shared/AppHeadingText.vue';
import HomeContentFaqBlock from '@/components/home/HomeContentFaqBlock.vue';

const DEFAULT_FAQ_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed at volutpat sapien. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. In hac habitasse platea dictumst. Nullam enim mi, tempus eget tortor non, lacinia imperdiet nibh. Morbi aliquam justo eu metus feugiat, quis feugiat turpis aliquam. Suspendisse malesuada arcu at mauris lobortis, ac ultricies nibh elementum. Aliquam erat volutpat. Quisque sollicitudin sem vel justo cursus pulvinar. Curabitur scelerisque efficitur pretium.";

const FAQ_TEXT = [
  {
    header: "How do you ensure the accuracy of the node ratings?",
    text: DEFAULT_FAQ_TEXT,
  },
  {
    header: "How often is the data updated on the dashboard?",
    text: DEFAULT_FAQ_TEXT,
  },
  {
    header: "What happens if a highly-rated node starts displaying malicious behavior?",
    text: DEFAULT_FAQ_TEXT,
  }
];


</script>

<template>
  <section class="home-content-faq">
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
