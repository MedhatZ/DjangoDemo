<template>
  <q-page class="flex flex-center q-pa-md">
    <div class="poc-panel q-pa-xl" style="width: 100%; max-width: 420px">
      <div class="poc-eyebrow q-mb-sm">Mock SSO placeholder</div>
      <h1 class="brand-mark text-h4 q-mt-none q-mb-sm">LexScope POC</h1>
      <p class="poc-muted q-mb-lg" style="margin-top: 0">
        Keycloak-style login stub only. Real SSO is assumed available at the client and
        intentionally out of scope for this demo.
      </p>

      <q-form class="poc-sans" @submit.prevent="onSubmit">
        <q-input
          v-model="username"
          label="Username"
          outlined
          dense
          class="q-mb-md"
          autocomplete="username"
        />
        <q-input
          v-model="password"
          label="Password"
          type="password"
          outlined
          dense
          class="q-mb-md"
          autocomplete="current-password"
          hint="Any non-empty password works in this POC"
        />
        <q-banner v-if="error" dense class="bg-negative text-white q-mb-md">
          {{ error }}
        </q-banner>
        <q-btn
          type="submit"
          color="primary"
          class="full-width"
          label="Sign in (mock token)"
          :loading="loading"
          no-caps
        />
      </q-form>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('demo.analyst')
const password = ref('demo')
const loading = ref(false)
const error = ref('')

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.replace(route.query.redirect || { name: 'inventory' })
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
