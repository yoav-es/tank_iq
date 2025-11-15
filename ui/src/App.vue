<!-- ui/src/App.vue -->
<template>
  <n-config-provider
    :theme-overrides="{
      Menu: {
        itemTextColor: '#ffffff',
        itemIconColor: '#ffffff',
        itemTextColorHover: '#3b82f6',
        itemIconColorHover: '#3b82f6',
        itemTextColorActive: '#3b82f6',
        itemIconColorActive: '#3b82f6',
        itemColorActive: 'rgba(59, 130, 246, 0.15)'
      }
    }"
  >
    <n-layout class="app-layout">
      <div class="shell-grid">
        <!-- Sidebar -->
        <aside class="sidebar">
          <div class="sidebar-header">
            <div class="header-title">TankIQ</div>
          </div>

          <n-menu
            mode="vertical"
            :options="menuOptions"
            :value="active"
            @update:value="onMenuSelect"
          />
        </aside>

        <!-- Main content -->
        <div class="main">
          <n-layout-header class="main-header" bordered />
          <n-layout-content class="main-content">
            <router-view />
          </n-layout-content>
        </div>
      </div>
    </n-layout>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLayoutStore } from './stores/layoutStore'

const router = useRouter()
const route = useRoute()
const layout = useLayoutStore()

const menuOptions = [
  { label: 'Fuel Log', key: 'entries' },
  { label: 'Statistics', key: 'stats' },
  { label: 'Add Entry', key: 'add-entry' }
]

const active = ref<string>(route.name as string ?? route.path)

function onMenuSelect(key: string): void {
  active.value = key
  layout.setMenu(key)
  const target = router.getRoutes().find(r => r.name === key)
  void router.push(target ? { name: key } : { path: `/${key}` })
}

watch(
  () => route.name,
  newName => {
    active.value = (newName as string) ?? route.path
    layout.setMenu(active.value)
  },
  { immediate: true }
)
</script>

<!-- No <style> here; all styles are in main.css -->