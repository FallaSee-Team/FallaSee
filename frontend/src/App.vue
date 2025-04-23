<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="row">
      <div class="col-md-4 col-12 logo">
        <RouterLink class="no-link" to="/">
        <h1>FallaSee</h1>
        <h3>Logical Fallacies<br> Detection</h3>
        </RouterLink>
      </div>
      <div class="col-md-8 col-12">
        <nav>
          <RouterLink to="/">Detection</RouterLink>
          <RouterLink to="/logical-fallacies">Fallacies</RouterLink>
          <RouterLink to="/game">Game</RouterLink>
      </nav>
      </div>
      
    </div>
  </header>

  <main>
    <RouterView />
  </main>
</template>

<style scoped>

</style>
