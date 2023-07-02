<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import IconCopy from "@/assets/icons/icon-copy.svg";
import { VIOLATIONS_MAP } from "@/utils/violations-map";
import useCopyToClipboard from "@/use/useCopyToClipboard";
import { useRequest } from "@/use/useRequest";
import { fetchTable } from "@/api/api-client";

const ORDER_MAP = {
  ascending: 'asc',
  descending: 'desc',
};

const { copyToClipboard } = useCopyToClipboard()
const { sendRequest: getTable, isLoading, data, error } = useRequest(fetchTable)

const violationsMap = Object.fromEntries(VIOLATIONS_MAP);

const tableData = ref([]);
const totalTableEntriesCount = ref(1000);
const tableState = reactive({
  currentPage: 1,
  pageSize: 10,
});
const tableSort = ref({});

const updateTableState = async (value, key) => {
  tableState[key] = value;
  console.log('tableState', tableState);
  await fetchTableData();
};
const updateTableSort = async ({ prop, order }) => {
  console.log('order_by', prop)
  console.log('sort_order', order)
  if (!order) {
    tableSort.value = {};
    await fetchTableData();
    return;
  }
  tableSort.value.order_by = prop;
  tableSort.value.sort_order = ORDER_MAP[order];
  console.log('tableSort', tableSort.value);
  await fetchTableData();
};

const checkIfCurrentPagePossible = computed( () => {
  return tableState.currentPage <= Math.ceil(totalTableEntriesCount.value / tableState.pageSize);
});

const fetchTableData = async () => {
  if (isLoading.value || !checkIfCurrentPagePossible.value) {
    return
  }
  await getTable([{
    page: tableState.currentPage,
    pagesize: tableState.pageSize,
    ...tableSort.value,
  }])
  if (error.value) {
    console.log('error', error.value)
    return
  }
  if (data.value) {
    totalTableEntriesCount.value = data.value.total
    tableData.value = [...data.value.data]
  }
};

const percentToHSL = (percent) => {
  const hue = 120 - (percent / 100) * 120;
  return { 'color': `hsl(${hue}, 100%, 30%)` }
}

const getViolationTooltip = ({ type, last_violation, violation_severity }) => {
  return `${violationsMap[type].description}` +
    `${last_violation ? `\nLast violation: ${last_violation}` : ''}` +
    `${violation_severity ? `\nSeverity: ${violation_severity}` : ''}`
}

onMounted(async () => {
  await fetchTableData();
});

</script>

<template>
  <section class="home-dashboard">
    <el-table
      :data="tableData"
      v-loading="isLoading"
      class="home-dashboard__table"
      @sort-change="updateTableSort"
    >
      <el-table-column
        prop="rank"
        label="Rank"
        width="90"
        sortable="custom"
      />
      <el-table-column
        label="Risk"
        prop="score"
        width="90"
        sortable="custom"
      >
        <template #default="{ row }">
          <span :style="percentToHSL(row.score)">
            {{ row.score }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column
        prop="address"
        label="Address"
      >
        <template #default="{ row }">
          <div class="home-dashboard__table-address">
            <div class="home-dashboard__table-address-text">
              {{ row.address }}
            </div>
            <IconCopy
              class="home-dashboard__table-address-copy"
              @click="copyToClipboard(row.address)"
            />
          </div>
        </template>
      </el-table-column>
      <el-table-column
        prop="name"
        label="Entity name"
        width="200"
      >
        <template #default="{ row }">
          <el-tag class="home-dashboard__table-entity">
            {{ row.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="blocks_created"
        label="Blocks"
        width="95"
        sortable="custom"
      >
        <template #default="{ row }">
          {{ (row.blocks_created * 100).toFixed(1) }}%
        </template>
      </el-table-column>
      <el-table-column
        prop="rank"
        label="Violations"
        class-name="home-dashboard__table-violations"
        min-width="115"
      >
        <template #default="{ row }">
          <el-tag
            v-for="(violation, index) in row.violations"
            :key="index + violation.type"
            class="home-dashboard__table-violation"
          >
            <el-tooltip
              effect="dark"
              :content="getViolationTooltip(violation)"
              placement="top"
              class="home-dashboard__table-violation-tooltip"
            >
              <div>
                <component :is="violationsMap[violation.type].icon" />
                <div class="home-dashboard__table-violation-text">
                  {{ violation.type }}
                </div>
              </div>
            </el-tooltip>
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="totalTableEntriesCount"
      class="home-dashboard__pagination"
      small
      layout="prev, pager, next, jumper, sizes"
      :total="totalTableEntriesCount"
      :page-sizes="[10, 20, 30, 40]"
      :pager-count="5"
      v-model:page-size="tableState.pageSize"
      v-model:current-page="tableState.currentPage"
      @size-change="updateTableState($event, 'pageSize')"
      @current-change="updateTableState($event, 'currentPage')"
    />
  </section>
</template>

<style lang="scss">
.home-dashboard {
  padding: 4rem 0;

  .home-dashboard__table {
    border: 1px solid var(--color-border);
    border-radius: 12px;
    --el-table-header-bg-color: var(--color-background-mute);
    --el-table-text-color: var(--color-text);
    --el-table-header-text-color: var(--color-text);
    --el-table-border: 0;

    table {
      font-size: 0.8rem;
    }

    thead {
      .cell {
        font-weight: 600;
      }
    }

    .home-dashboard__table-address {
      display: grid;
      grid-template-columns: auto 1fr;
      align-items: center;

      .home-dashboard__table-address-text {
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
      }

      .home-dashboard__table-address-copy {
        cursor: pointer;
        margin-left: 0.2rem;
      }
    }

    .home-dashboard__table-entity {
      color: var(--color-text);
      background: var(--color-background-mute);
      border: 0;
    }

    .home-dashboard__table-violations {
      .cell {
        display: flex;
        flex-flow: row wrap;
        gap: 0.4rem;
        .el-tag {
          --el-tag-text-color: var(--color-text-danger);
          --el-tag-bg-color: var(--color-background-danger);
          border: 0;
        }
      }
    }

    .home-dashboard__table-violation {
      padding: 0.3rem 0.3rem;
      font-weight: 500;
      cursor: help;

      .home-dashboard__table-violation-text{
        display: none;
      }

      @media (min-width: 1050px) {
        .home-dashboard__table-violation-text{
          display: inline-block;
          height: 100%;
        }
      }

      & > .el-tag__content {
        & > .el-tooltip__trigger {
          display: flex;
          align-items: center;
          gap: 0.2rem;
        }
      }
    }
  }

  .home-dashboard__pagination {
    margin-top: 1rem;
  }
}
</style>
