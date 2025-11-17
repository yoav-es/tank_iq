<template>
  <section class="dashboard">
    <h1>Dashboard</h1>

    <div class="graph-container">
      <h2>Average Fuel Consumption</h2>
      <img :src="dummyGraph" alt="Fuel Consumption Graph" class="graph-image" />
    </div>

    <div class="cards-grid">
      <div class="card"><h3>Current Avg</h3><p>6.8 L/100km</p></div>
      <div class="card"><h3>Best Month</h3><p>5.9 L/100km</p></div>
      <div class="card"><h3>Total Distance</h3><p>2450 km</p></div>
      <div class="card"><h3>Total Fuel</h3><p>320 L</p></div>
      <div class="card"><h3>Avg Cost</h3><p>$1.45/L</p></div>
      <div class="card"><h3>Trips Logged</h3><p>42</p></div>
    </div>
  </section>
</template>

<script setup lang="ts">
import dummyGraph from '../assets/dummy_graph.png';
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-2xl); /* consistent spacing */
}

/* Graph Section */
.graph-container {
  background: var(--color-card);
  padding: var(--space-lg);
  border-radius: 8px;
}

.graph-image {
  width: 100%;
  max-height: 400px; /* enlarged graph */
  object-fit: contain;
  border-radius: 6px;
}

/* Cards Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

.card {
  background: var(--color-card);
  border-radius: 8px;
  padding: var(--space-md);
  text-align: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}

.card h3 {
  color: var(--color-secondary);
  margin-bottom: var(--space-sm);
}

/* Responsive */
@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 480px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>