<script setup>
import { onMounted, ref, shallowRef } from 'vue';
import { fetchMinerDistribution } from '@/api/api-client';
import { useRequest } from '@/use/useRequest';
import Chart from 'chart.js/auto';

const chart = ref(null);
const chartData = ref(null);
const { sendRequest: getMinerDistribution, isLoading, data, error } = useRequest(fetchMinerDistribution);


const pieChart = shallowRef(null)
const fetchChartData = async () => {
  if (isLoading.value) {
    return;
  }

  await getMinerDistribution();
  if (error.value) {
    return;
  }
  if (data.value) {
    chartData.value = data.value;
    console.log('data', data.value);
  }
};

onMounted(async () => {
  await fetchChartData();
  pieChart.value = new Chart(chart.value, {
    type: 'pie',
    data: {
      datasets: [chartData.value.pie_chart],
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
