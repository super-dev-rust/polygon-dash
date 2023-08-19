<script setup>
import { onMounted, ref, shallowRef } from 'vue';
import Chart from 'chart.js/auto';

const isLoading = ref(false);
const chart = ref(null);
const chartData = ref({
  labels: [
    'Red',
    'Blue',
    'Yellow'
  ],
  datasets: [{
    label: 'My First Dataset',
    data: [300, 50, 100],
    backgroundColor: [
      'rgb(255, 99, 132)',
      'rgb(54, 162, 235)',
      'rgb(255, 205, 86)'
    ],
    hoverOffset: 4
  }]
});
const pieChart = shallowRef(null)

onMounted(async () => {
  // await fetchChartData();
  pieChart.value = new Chart(chart.value, {
    type: 'pie',
    data: {
      labels: chartData.value.labels,
      datasets: chartData.value.datasets,
    },
    options: {
      responsive: true,
    }
  });
  console.log('pieChart', pieChart);
});
</script>

<template>
  <div class="home-content-pie-chart" v-loading="isLoading">
    <canvas v-if="chartData" ref="chart" />
  </div>
</template>

<style lang="scss">
.home-content-pie-chart {
  position: relative;
}
</style>
