<template>
  <q-layout view="hHh Lpr lFf" class="poc-shell">
    <q-header elevated class="poc-topbar">
      <q-toolbar class="q-px-md">
        <div class="column q-py-sm">
          <div class="brand-mark text-h6" style="line-height: 1.1">LexScope POC</div>
          <div class="text-caption" style="opacity: 0.8; font-family: 'IBM Plex Sans', sans-serif">
            Legislative &amp; regulatory reporting proof of concept
          </div>
        </div>
        <q-space />
        <q-tabs dense stretch active-color="white" indicator-color="accent" class="poc-sans">
          <q-route-tab name="inventory" label="Inventory Builder" :to="{ name: 'inventory' }" />
          <q-route-tab name="comparison" label="Comparison Builder" :to="{ name: 'comparison' }" />
        </q-tabs>
        <q-separator vertical dark class="q-mx-md" />
        <div class="poc-sans text-caption q-mr-md" style="opacity: 0.85">
          {{ auth.user?.username || 'analyst' }}
          <span style="opacity: 0.6"> · mock SSO</span>
        </div>
        <q-btn flat dense label="Logout" class="poc-sans" @click="onLogout" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function onLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>
