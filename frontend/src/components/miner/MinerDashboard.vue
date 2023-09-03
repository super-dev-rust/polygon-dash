<script setup>
import { onMounted, ref, shallowRef } from 'vue';
import { useRouter } from 'vue-router';
import { useRequest } from '@/use/useRequest';
import { fetchMiner } from '@/api/api-client';
import Chart from 'chart.js/auto';

const DEFAULT_CONFIG = {
  scales: {
    y: {
      beginAtZero: true,
      type: 'logarithmic',
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
};

const router = useRouter();
const { sendRequest: getChart, isLoading, data, error } = useRequest(fetchMiner);

const chart = ref(null);
const chartData = ref(null);
const chartArgs = ref({});
const selectModel = ref(250)
const myChart = shallowRef(null)

const selectOptions = [
  { value: 250, label: '250' },
  { value: 500, label: '500' },
  { value: 750, label: '750' },
  { value: 1000, label: '1000' },
]

const fetchChartData = async () => {
  if (isLoading.value) {
    return;
  }
  const address = router.currentRoute.value.params.address;
  chartArgs.value = {
    last_blocks: selectModel.value,
  }
  console.log('chartArgs', chartArgs.value)
  await getChart([
    {
      address,
      params: { ...chartArgs.value }
    }
  ]);
  if (error.value) {
    return;
  }
  if (data.value) {
    chartData.value = data.value;
    console.log('data', data.value.datasets);
  }
};

const updateData = (datasets, labels) => {
  myChart.value.data.datasets = datasets;
  myChart.value.data.labels = labels;
  myChart.value.update();
}
const updateChart = async () => {
  await fetchChartData();
  updateData(chartData.value.datasets, chartData.value.labels);
}

onMounted(async () => {
  await fetchChartData();
  const gradientLine = chart.value.getContext('2d').createLinearGradient(0, 0, 0, 400);
  gradientLine.addColorStop(0, 'green');
  gradientLine.addColorStop(0.5, 'yellow');
  gradientLine.addColorStop(1, 'red');
  const lineDataset = chartData.value.datasets.find((dataset) => dataset.type === 'line');
  if (lineDataset) {
    lineDataset.backgroundColor = gradientLine;
    lineDataset.borderColor = gradientLine;
  }

  myChart.value = new Chart(chart.value, {
    type: 'bar',
    data: {
      labels: chartData.value.labels,
      datasets: chartData.value.datasets,
    },
    options: chartData.value.options ? chartData.value.options : DEFAULT_CONFIG,
  });
  console.log('myChart', myChart);
});
</script>

<template>
  <el-select v-model="selectModel" class="m-2" placeholder="50" @change="updateChart">
    <el-option v-for="item in selectOptions" :key="item.value" :label="item.label" :value="item.value">
    </el-option>
  </el-select>
  <div v-loading="isLoading">
    <canvas v-if="chartData" ref="chart" />
  </div>
</template>

<style scoped></style>
