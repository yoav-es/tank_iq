<template>
  <n-card title="Fuel Statistics" bordered>
    <n-space vertical v-if="store.detailedStats">
      <n-statistic
        label="Total Distance"
        :value="store.detailedStats.overall_stats.total_distance + ' km'"
      />
      <n-statistic
        label="Total Liters"
        :value="store.detailedStats.overall_stats.total_liters + ' L'"
      />
      <n-statistic
        label="Total Cost"
        :value="'$' + store.detailedStats.overall_stats.total_cost"
      />
      <n-statistic
        label="Average Km/L"
        :value="store.detailedStats.overall_stats.average_km_per_liter"
      />
      <n-statistic
        label="Average Cost/L"
        :value="'$' + store.detailedStats.overall_stats.average_cost_per_liter"
      />
    </n-space>

    <n-alert v-else type="info" title="Loading stats...">
      Please wait while we fetch your fuel statistics.
    </n-alert>
  </n-card>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useFuelStore } from '../stores/fuelStore';

// ✅ Correct imports for v2.43.1
import { NCard, NSpace, NAlert, NStatistic } from 'naive-ui';

const store = useFuelStore();

onMounted(() => {
  store.fetchDetailedStats();
});
</script>