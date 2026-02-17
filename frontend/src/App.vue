<template>
  <Navbar /> <main class="container">
    <router-view /> </main>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue';
</script>

<style>
.container { padding: 20px; max-width: 1200px; margin: 0 auto; }
</style>