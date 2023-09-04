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

const setGradientLine = (dataset) => {
  const yAxis = myChart.value.scales.y;
  const indexOf1 = yAxis.ticks.findIndex((tick) => tick.value === 1);
  const pixelHeight = yAxis.getPixelForTick(indexOf1);
  const gradientLine = chart.value.getContext('2d').createLinearGradient(0, pixelHeight, 0, yAxis.getPixelForTick(0));
  gradientLine.addColorStop(0, 'green');
  gradientLine.addColorStop(0.16, 'yellow');
  gradientLine.addColorStop(0.37, 'red');
  dataset.backgroundColor = gradientLine;
  dataset.borderColor = gradientLine;
}

const getGradientLineLabelColor = () => {
  const gradientFill = chart.value.getContext('2d').createLinearGradient(0, 0, 0, 33);
  gradientFill.addColorStop(0, 'green');
  gradientFill.addColorStop(0.5, 'yellow');
  gradientFill.addColorStop(1, 'red');
  return gradientFill;
}

const fetchChartData = async () => {
  if (isLoading.value) {
    return;
  }
  const address = router.currentRoute.value.params.address;
  chartArgs.value = {
    last_blocks: selectModel.value,
  }
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
  }
};

const updateData = (datasets, labels) => {
  const lineDataset = datasets.find((dataset) => dataset.type === 'line');
  if (lineDataset) {
    setGradientLine(lineDataset);
  }
  myChart.value.data.datasets = datasets;
  myChart.value.data.labels = labels;
  myChart.value.update();
}
const updateChart = async () => {
  await fetchChartData();
  updateData(chartData.value.datasets, chartData.value.labels);
}

const updateChartGradient = () => {
  const lineDataset = chartData.value.datasets.find((dataset) => dataset.type === 'line');
  if (lineDataset) {
    setGradientLine(lineDataset);
    myChart.value.update();
  }
}

onMounted(async () => {
  await fetchChartData();
  myChart.value = new Chart(chart.value, {
    type: 'bar',
    data: {
      labels: chartData.value.labels,
      datasets: chartData.value.datasets,
    },
    options: {
      ...(chartData.value.options ? chartData.value.options : DEFAULT_CONFIG),
      plugins: {
        legend: {
          onClick: async (evt, legendItem, legend) => {
            Chart.defaults.plugins.legend.onClick(evt, legendItem, legend)
            updateChartGradient();
          },
          labels: {
            generateLabels: (chart) => {
              let defaultLabels = Chart.defaults.plugins.legend.labels.generateLabels(chart);
              defaultLabels[0].fillStyle = getGradientLineLabelColor();
              return defaultLabels;
            }
          }
        }
      },
    },
  });

  updateChartGradient();
  console.log('myChart', myChart);
});
</script>

<template>
  <div class="miner-dashboard">
    <el-select v-model="selectModel" class="m-2" placeholder="50" @change="updateChart">
      <el-option v-for="item in selectOptions" :key="item.value" :label="item.label" :value="item.value">
      </el-option>
    </el-select>
    <div v-loading="isLoading" class="miner-dashboard__chart-container">
      <canvas v-if="chartData" ref="chart" class="miner-dashboard__chart" @onDatasetHidden="updateChartGradient"
        @onDatasetShown="updateChartGradient" />
    </div>
  </div>
</template>

<style lang="scss">
@import "@/assets/colors.scss";

.miner-dashboard {
  padding-bottom: 2rem;

  .miner-dashboard__chart-container {
    position: relative;
  }

  .miner-dashboard__chart {
    background: $base-white;
  }
}
</style>
