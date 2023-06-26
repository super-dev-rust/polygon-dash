<template>
  <header class="guardian-header">
    <IconGuardian />
  </header>
</template>

<script>
import IconGuardian from "@/assets/icons/icon-guardian.svg";

export default {
  name: "AppHeader",
  components: {
    IconGuardian,
  },
}
</script>

<style lang="scss">
.guardian-header {
  height: 96px;
}
</style>
