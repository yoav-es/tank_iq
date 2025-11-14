<template>
  <n-layout>
    <n-layout-header bordered>
      <n-menu
        mode="horizontal"
        :options="menuOptions"
        :value="active"
        @update:value="onMenuSelect"
      />
    </n-layout-header>

    <n-layout-content style="padding: 24px">
      <router-view /> <!-- This renders the current route's component -->
    </n-layout-content>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { NLayout, NLayoutHeader, NLayoutContent, NMenu } from 'naive-ui';

const router = useRouter();
const route = useRoute();

const active = ref(route.path); // sync menu with current route

const menuOptions = [
  { label: 'Fuel Log', key: '/' },
  { label: 'Statistics', key: '/stats' },
  { label: 'Add Entry', key: '/entry/add' },
];

function onMenuSelect(key: string) {
  active.value = key;
  router.push(key);
}

// keep menu active state in sync with route changes
watch(route, () => {
  active.value = route.path;
});
</script>