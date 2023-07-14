<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useRequest } from '@/use/useRequest';
import { fetchMiner } from '@/api/api-client';
import Chart from 'chart.js/auto';

const router = useRouter();
const { sendRequest: getChart, isLoading, data, error } = useRequest(fetchMiner);

const chart = ref(null);
const chartData = ref(null);
const fetchChartData = async () => {
  if (isLoading.value) {
    return;
  }
  const address = router.currentRoute.value.params.address;
  await getChart([address]);
  if (error.value) {
    return;
  }
  if (data.value) {
    chartData.value = data.value;
    console.log('data', data.value.datasets);
  }
};

onMounted(async () => {
  await fetchChartData();
  console.log('chart', chart.value);
  const myChart = new Chart(chart.value, {
    type: 'bar',
    data: {
      labels: chartData.value.labels,
      datasets: chartData.value.datasets,
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          stacked: true
        },
        x: {
          beginAtZero: true,
          stacked: true
        }
      },

      responsive: true,

      legend: {
        labels: {
          fontColor: 'red',
        }
      }
    }
  });
  console.log('myChart', myChart);
});
</script>

<template>
  <canvas v-if="chartData" ref="chart"></canvas>
</template>

<style scoped>

</style>
