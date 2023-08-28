<script setup>
import { onMounted, ref, shallowRef } from 'vue';
import { fetchMinerDistribution } from '@/api/api-client';
import { useRequest } from '@/use/useRequest';
import Chart from 'chart.js/auto';

const chart = ref(null);
const chartData = ref(null);
const { sendRequest: getMinerDistribution, isLoading, data, error } = useRequest(fetchMinerDistribution);



// const chartData = ref({
//   labels: [
//     'Red',
//     'Blue',
//     'Yellow'
//   ],
//   datasets: [{
//     label: 'My First Dataset',
//     data: [300, 50, 100],
//     backgroundColor: [
//       'rgb(255, 99, 132)',
//       'rgb(54, 162, 235)',
//       'rgb(255, 205, 86)'
//     ],
//     hoverOffset: 4
//   }]
// });
const pieChart = shallowRef(null)
const fetchChartData = async () => {
  console.log('isLgfdgdf');
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
      labels: chartData.value.labels,
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
