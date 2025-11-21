<template>
  <section class="stats">
    <h1 class="page-title">📈 Statistics</h1>
    <div class="card">
      <p>This is a placeholder for the Statistics view.</p>
      <p>You can decide later what graphs or data to show here.</p>
    </div>
  </section>
</template>

<script setup lang="ts">
// Dummy view — no chart logic yet
</script>

<style scoped>
.page-title {
  font-size: 2rem;
  font-weight: bold;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: var(--space-xs);
}

.stats {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.card {
  background: var(--color-card);
  padding: var(--space-md);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>