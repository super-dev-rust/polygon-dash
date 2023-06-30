<script setup>
import { computed, reactive, ref } from "vue";
import IconCopy from "@/assets/icons/icon-copy.svg";
import { UNTRUSTED_NODES_MOCK} from "@/utils/mocks/home-dasboard-example";
import { VIOLATIONS_MAP } from "@/utils/violations-map";
import useCopyToClipboard from "@/use/useCopyToClipboard";
import { useRequest } from "@/use/useRequest";
import { fetchTable } from "@/api/api-client";

const { copyToClipboard } = useCopyToClipboard()
const { sendRequest: getTable, isLoading, data, error } = useRequest(fetchTable)

const violationsMap = Object.fromEntries(VIOLATIONS_MAP);

const tableData = ref([]);
const totalTableEntriesCount = ref(1000);
const tableState = reactive({
  currentPage: 1,
  pageSize: 10,
});

const updateTableState = async (value, key) => {
  tableState[key] = value;
  console.log('tableState', tableState);
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
    perPage: tableState.pageSize,
  }])
  if (error.value) {
    console.log('error', error.value)
    return
  }
  if (data.value) {
    totalTableEntriesCount.value = data.value.total
    tableData.value = [...data.value]
  }
};

function percentToHSL(percent) {
  const hue = (percent / 100) * 120;
  return { 'color': `hsl(${hue}, 100%, 30%)` }
}

</script>

<template>
  <section class="home-dashboard">
    <el-table
      :data="UNTRUSTED_NODES_MOCK"
      :default-sort="{ prop: 'rank', order: 'descending' }"
      class="home-dashboard__table"
    >
      <el-table-column
        prop="rank"
        label="Rank"
        width="90"
        sortable
      />
      <el-table-column
        label="Trust"
        prop="score"
        width="90"
        sortable
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
        sortable
      >
        <template #default="{ row }">
          {{ row.blocks_created }}%
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
            :key="index + violation"
            class="home-dashboard__table-violation"
          >
            <el-tooltip
              effect="dark"
              :content="violationsMap[violation].description"
              placement="top"
              class="home-dashboard__table-violation-tooltip"
            >
              <div>
                <component :is="violationsMap[violation].icon" />
                <div class="home-dashboard__table-violation-text">
                  {{ violation }}
                </div>
              </div>
            </el-tooltip>
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
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
