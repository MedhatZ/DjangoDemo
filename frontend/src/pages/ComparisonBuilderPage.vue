<template>
  <q-page class="q-pa-md q-pa-md-lg">
    <div class="row items-end q-col-gutter-md q-mb-md">
      <div class="col">
        <div class="poc-eyebrow">Side-by-side matrix</div>
        <h1 class="brand-mark text-h4 q-my-xs">Regulatory Comparison Builder</h1>
        <p class="poc-muted q-ma-none">
          Multi-jurisdiction selection · structured fields · save config · Excel export
        </p>
      </div>
    </div>

    <div class="row q-col-gutter-md">
      <!-- Config panel -->
      <div class="col-12 col-md-4">
        <div class="poc-panel q-pa-md poc-sans">
          <div class="text-subtitle2 q-mb-md">Comparison setup</div>

          <q-select
            v-model="form.jurisdictions"
            :options="meta.jurisdictions"
            label="Jurisdictions"
            outlined
            dense
            multiple
            use-chips
            class="q-mb-md"
            hint="Select 2+ for a meaningful matrix"
          />

          <q-select
            v-model="form.topic"
            :options="meta.topics"
            label="Topic (optional filter)"
            outlined
            dense
            clearable
            class="q-mb-md"
          />

          <q-select
            v-model="form.fields"
            :options="meta.comparison_fields"
            label="Structured fields"
            outlined
            dense
            multiple
            use-chips
            class="q-mb-md"
          />

          <q-input
            v-model="form.name"
            label="Config name (to save)"
            outlined
            dense
            class="q-mb-md"
          />

          <div class="row q-gutter-sm q-mb-md">
            <q-btn color="primary" label="Build matrix" no-caps :loading="loading" @click="preview" />
            <q-btn outline color="primary" label="Save config" no-caps :disable="!form.name" @click="saveConfig" />
            <q-btn flat color="accent" icon="download" label="Excel" no-caps :disable="!matrix" @click="exportExcel" />
          </div>

          <q-separator class="q-my-md" />

          <div class="text-subtitle2 q-mb-sm">Saved configurations</div>
          <q-list bordered separator dense v-if="saved.length">
            <q-item
              v-for="c in saved"
              :key="c.id"
              clickable
              @click="loadConfig(c)"
            >
              <q-item-section>
                <q-item-label>{{ c.name }}</q-item-label>
                <q-item-label caption>
                  {{ (c.jurisdictions || []).join(', ') }}
                  <span v-if="c.topic"> · {{ c.topic }}</span>
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-btn flat dense round icon="delete" size="sm" @click.stop="removeConfig(c.id)" />
              </q-item-section>
            </q-item>
          </q-list>
          <div v-else class="text-caption poc-muted">No saved configs yet.</div>
        </div>
      </div>

      <!-- Matrix -->
      <div class="col-12 col-md-8">
        <div class="poc-panel q-pa-md" style="overflow: auto; max-height: calc(100vh - 180px)">
          <div v-if="!matrix" class="poc-muted poc-sans q-pa-lg text-center">
            Choose jurisdictions and build the comparison matrix.
          </div>
          <template v-else>
            <div class="poc-sans text-caption poc-muted q-mb-sm">
              {{ matrix.column_count }} columns · {{ matrix.fields?.length || 0 }} fields
            </div>
            <table class="matrix-table" style="width: 100%; border-collapse: collapse">
              <thead>
                <tr>
                  <th style="padding: 10px; text-align: left; min-width: 140px">Field</th>
                  <th
                    v-for="col in matrix.columns"
                    :key="col.id"
                    style="padding: 10px; text-align: left; min-width: 160px"
                  >
                    <div>{{ col.jurisdiction }}</div>
                    <div style="font-weight: 400; opacity: 0.85; font-size: 0.75rem">
                      {{ col.code }} · {{ col.status }}
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in matrix.matrix" :key="row.field">
                  <td style="padding: 10px; border-bottom: 1px solid #e2e8f0">
                    {{ labelField(row.field) }}
                  </td>
                  <td
                    v-for="cell in row.cells"
                    :key="cell.legislation_id"
                    style="padding: 10px; border-bottom: 1px solid #e2e8f0"
                  >
                    {{ cell.value || '—' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </template>
        </div>
      </div>
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
  comparison_fields: []
})

const form = reactive({
  name: '',
  jurisdictions: ['Germany', 'France', 'UK'],
  topic: 'AI',
  fields: [
    'scope',
    'enforcement_authority',
    'penalty_max',
    'reporting_obligation',
    'cross_border_rules',
    'status'
  ]
})

const matrix = ref(null)
const saved = ref([])
const loading = ref(false)

function labelField(f) {
  return f.replaceAll('_', ' ')
}

async function loadMeta() {
  const { data } = await api.get('/api/legislation/meta')
  meta.jurisdictions = data.jurisdictions
  meta.topics = data.topics
  meta.comparison_fields = data.comparison_fields
}

async function loadSaved() {
  const { data } = await api.get('/api/comparisons')
  saved.value = Array.isArray(data) ? data : data.results || []
}

async function preview() {
  if (!form.jurisdictions.length) {
    $q.notify({ type: 'warning', message: 'Select at least one jurisdiction' })
    return
  }
  loading.value = true
  try {
    const { data } = await api.post('/api/comparisons/preview', {
      jurisdictions: form.jurisdictions,
      topic: form.topic || null,
      fields: form.fields
    })
    matrix.value = data
  } catch (e) {
    $q.notify({
      type: 'negative',
      message: e?.response?.data?.detail || 'Preview failed'
    })
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  try {
    await api.post('/api/comparisons', {
      name: form.name,
      topic: form.topic || '',
      jurisdictions: form.jurisdictions,
      fields: form.fields,
      notes: 'Saved from Comparison Builder POC'
    })
    $q.notify({ type: 'positive', message: 'Comparison config saved' })
    form.name = ''
    await loadSaved()
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Save failed' })
  }
}

async function loadConfig(c) {
  form.name = c.name
  form.jurisdictions = [...(c.jurisdictions || [])]
  form.topic = c.topic || null
  form.fields = [...(c.fields || meta.comparison_fields)]
  await preview()
}

async function removeConfig(id) {
  await api.delete(`/api/comparisons/${id}`)
  await loadSaved()
  $q.notify({ type: 'info', message: 'Config deleted' })
}

async function exportExcel() {
  try {
    $q.loading.show({ message: 'Exporting Excel…' })
    const response = await api.post(
      '/api/comparisons/preview',
      {
        jurisdictions: form.jurisdictions,
        topic: form.topic || null,
        fields: form.fields,
        format: 'xlsx'
      },
      { responseType: 'blob' }
    )
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'regulatory_comparison.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    $q.notify({ type: 'negative', message: 'Excel export failed' })
  } finally {
    $q.loading.hide()
  }
}

onMounted(async () => {
  await loadMeta()
  await loadSaved()
  await preview()
})
</script>
