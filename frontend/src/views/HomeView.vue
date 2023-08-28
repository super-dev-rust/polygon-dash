<script setup>
import HomeContentRouter from "@/components/home/HomeContentRouter.vue";
import HomeDashboard from "@/components/home/HomeDashboard.vue";
import HomeContentTrustScore from '@/components/home/HomeContentTrustScore.vue';
import HomeContentSteps from '@/components/home/HomeContentSteps.vue';
import HomeContentAbout from '@/components/home/HomeContentAbout.vue';
import HomeContentFaq from '@/components/home/HomeContentFaq.vue';
</script>

<template>
  <main>
    <HomeContentRouter />
    <HomeDashboard />
    <HomeContentTrustScore />
    <HomeContentSteps />
    <HomeContentAbout />
    <HomeContentFaq />
  </main>
</template>
