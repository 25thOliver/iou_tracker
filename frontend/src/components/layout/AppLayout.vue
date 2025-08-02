<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Sidebar -->
    <Sidebar 
      :is-open="sidebarOpen" 
      @close="sidebarOpen = false"
    />
    
    <!-- Main content area -->
    <div class="flex-1 flex flex-col lg:ml-64">
      <!-- Top navigation -->
      <TopNavbar @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      
      <!-- Main content -->
      <main class="flex-1 p-4 lg:p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import TopNavbar from './TopNavbar.vue'

const sidebarOpen = ref(false)
</script>
