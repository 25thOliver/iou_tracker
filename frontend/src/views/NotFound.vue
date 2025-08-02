<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <div class="mx-auto h-24 w-24 text-gray-400">
          <ExclamationTriangleIcon class="h-full w-full" />
        </div>
        <h1 class="mt-6 text-6xl font-bold text-gray-900">404</h1>
        <h2 class="mt-2 text-2xl font-medium text-gray-900">
          Page not found
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Sorry, we couldn't find the page you're looking for.
        </p>
      </div>
      
      <div class="mt-8 flex justify-center space-x-4">
        <router-link
          to="/dashboard"
          class="btn-primary"
        >
          Go to Dashboard
        </router-link>
        <button
          @click="goBack"
          class="btn-secondary"
        >
          Go Back
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>
