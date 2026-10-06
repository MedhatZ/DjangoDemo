<template>
  <q-page class="q-pa-md q-pa-md-lg">
    <div class="row items-end q-col-gutter-md q-mb-md">
      <div class="col">
        <div class="poc-eyebrow">Reporting surface</div>
        <h1 class="brand-mark text-h4 q-my-xs">Legislative Inventory Builder</h1>
        <p class="poc-muted q-ma-none">
          Filter · sort · paginate · include/exclude records · export CSV / Excel
        </p>
      </div>
      <div class="col-auto poc-sans">
        <q-btn-dropdown color="accent" label="Export" icon="download" no-caps>
          <q-list>
            <q-item v-close-popup clickable @click="exportReport('csv')">
              <q-item-section>Export CSV</q-item-section>
            </q-item>
            <q-item v-close-popup clickable @click="exportReport('xlsx')">
              <q-item-section>Export Excel</q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </div>
    </div>

    <!-- Filters row -->
    <div class="poc-panel q-pa-md q-mb-md">
      <div class="row q-col-gutter-md items-end poc-sans">
        <div class="col-12 col-sm-4 col-md-3">
          <q-select
            v-model="filters.jurisdiction"
            :options="meta.jurisdictions"
            label="Jurisdiction"
            outlined
            dense
            clearable
            emit-value
            map-options
          />
        </div>
        <div class="col-12 col-sm-4 col-md-3">
          <q-select
            v-model="filters.topic"
            :options="meta.topics"
            label="Topic"
            outlined
            dense
            clearable
          />
        </div>
        <div class="col-12 col-sm-4 col-md-3">
          <q-select
            v-model="filters.status"
            :options="meta.statuses"
            label="Status"
            outlined
            dense
            clearable
          />
        </div>
        <div class="col-12 col-md-3 flex q-gutter-sm">
          <q-btn color="primary" label="Apply" no-caps @click="applyFilters" />
          <q-btn flat label="Reset" no-caps @click="resetFilters" />
        </div>
      </div>
      <div v-if="aggregates" class="poc-sans text-caption q-mt-md poc-muted">
        {{ total }} matching ·
        <template v-for="(n, k) in aggregates.by_status" :key="k">
          {{ k }}: {{ n }}&nbsp;&nbsp;
        </template>
        <span v-if="excludedIds.length"> · {{ excludedIds.length }} excluded from export</span>
      </div>
    </div>

    <!-- Table -->
    <div class="poc-panel">
      <q-table
        v-model:pagination="pagination"
        class="poc-sans"
        flat
        row-key="id"
        :rows="rows"
        :columns="columns"
        :loading="loading"
        :rows-per-page-options="[5, 10, 25]"
        binary-state-sort
        @request="onRequest"
      >
        <template #body-cell-include="props">
          <q-td :props="props">
            <q-checkbox
              :model-value="!excludedIds.includes(props.row.id)"
              dense
              @update:model-value="(v) => toggleInclude(props.row.id, v)"
            />
          </q-td>
        </template>
        <template #body-cell-status="props">
          <q-td :props="props">
            <q-badge
              :color="statusColor(props.row.status)"
              :label="props.row.status"
              outline
            />
          </q-td>
        </template>
      </q-table>
    </div>
  </q-page>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '@/services/api'

const $q = useQuasar()

const meta = reactive({
  jurisdictions: [],
  topics: [],
  statuses: []
})

const filters = reactive({
  jurisdiction: null,
  topic: null,
  status: null
})

const rows = ref([])
const total = ref(0)
const aggregates = ref(null)
const loading = ref(false)
const excludedIds = ref([])
const allFilteredIds = ref([])

const pagination = ref({
  sortBy: 'jurisdiction',
  descending: false,
  page: 1,
  rowsPerPage: 10,
  rowsNumber: 0
})

const columns = [
  { name: 'include', label: 'Incl.', field: 'id', align: 'center', style: 'width: 56px' },
  { name: 'code', label: 'Code', field: 'code', align: 'left', sortable: true },
  { name: 'title', label: 'Title', field: 'title', align: 'left', sortable: true },
  { name: 'jurisdiction', label: 'Jurisdiction', field: 'jurisdiction', align: 'left', sortable: true },
  { name: 'topic', label: 'Topic', field: 'topic', align: 'left', sortable: true },
  { name: 'status', label: 'Status', field: 'status', align: 'left', sortable: true },
  { name: 'effective_date', label: 'Effective', field: 'effective_date', align: 'left', sortable: true },
  { name: 'issuing_body', label: 'Issuing body', field: 'issuing_body', align: 'left' }
]

function statusColor(s) {
  if (s === 'Active') return 'positive'
  if (s === 'Proposed') return 'warning'
  return 'grey-7'
}

function filterParams() {
  const p = {}
  if (filters.jurisdiction) p.jurisdiction = filters.jurisdiction
  if (filters.topic) p.topic = filters.topic
  if (filters.status) p.status = filters.status
  return p
}

function orderingFromPagination(pag) {
  if (!pag.sortBy) return undefined
  return pag.descending ? `-${pag.sortBy}` : pag.sortBy
}

async function loadMeta() {
  const { data } = await api.get('/api/legislation/meta')
  meta.jurisdictions = data.jurisdictions
  meta.topics = data.topics
  meta.statuses = data.statuses
}

async function fetchPage(pag = pagination.value) {
  loading.value = true
  try {
    const params = {
      ...filterParams(),
      page: pag.page,
      page_size: pag.rowsPerPage,
      ordering: orderingFromPagination(pag)
    }
    const { data } = await api.get('/api/legislation', { params })
    rows.value = data.results
    total.value = data.count
    pagination.value.rowsNumber = data.count
    pagination.value.page = pag.page
    pagination.value.rowsPerPage = pag.rowsPerPage
    pagination.value.sortBy = pag.sortBy
    pagination.value.descending = pag.descending

    // Full filtered set for exclude/export (no pagination)
    const inv = await api.get('/api/reports/inventory', { params: filterParams() })
    aggregates.value = inv.data.aggregates
    allFilteredIds.value = inv.data.results.map((r) => r.id)
  } catch (e) {
    $q.notify({ type: 'negative', message: e?.response?.data?.detail || 'Failed to load inventory' })
  } finally {
    loading.value = false
  }
}

function onRequest(props) {
  fetchPage(props.pagination)
}

function applyFilters() {
  excludedIds.value = []
  pagination.value.page = 1
  fetchPage(pagination.value)
}

function resetFilters() {
  filters.jurisdiction = null
  filters.topic = null
  filters.status = null
  excludedIds.value = []
  applyFilters()
}

function toggleInclude(id, included) {
  if (included) {
    excludedIds.value = excludedIds.value.filter((x) => x !== id)
  } else if (!excludedIds.value.includes(id)) {
    excludedIds.value = [...excludedIds.value, id]
  }
}

async function exportReport(format) {
  try {
    $q.loading.show({ message: `Building ${format.toUpperCase()}…` })
    const params = {
      ...filterParams(),
      format,
      ordering: orderingFromPagination(pagination.value)
    }
    if (excludedIds.value.length) {
      params.exclude_ids = excludedIds.value.join(',')
    }
    const response = await api.get('/api/reports/inventory', {
      params,
      responseType: 'blob'
    })
    const ext = format === 'csv' ? 'csv' : 'xlsx'
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `legislative_inventory.${ext}`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Export failed' })
  } finally {
    $q.loading.hide()
  }
}

onMounted(async () => {
  await loadMeta()
  await fetchPage()
})
</script>
