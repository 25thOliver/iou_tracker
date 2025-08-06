<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-900">IOU Tracker</h1>
        <h2 class="mt-6 text-2xl font-medium text-gray-900">
          Sign in to your account
        </h2>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Error message -->
          <div
            v-if="authStore.error"
            class="rounded-md bg-red-50 p-4 border border-red-200"
          >
            <div class="text-sm text-red-700">
              {{ authStore.error }}
            </div>
          </div>

          <!-- Username or Email field -->
          <div>
            <label for="username_or_email" class="block text-sm font-medium text-gray-700">
              Username or Email
            </label>
            <div class="mt-1">
              <input
                id="username_or_email"
                v-model="form.username_or_email"
                type="text"
                autocomplete="username"
                required
                class="input-field"
                :class="{ 'border-red-300': errors.username_or_email }"
              />
              <p v-if="errors.username_or_email" class="mt-1 text-sm text-red-600">
                {{ errors.username_or_email }}
              </p>
            </div>
          </div>

          <!-- Password field -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div class="mt-1">
              <input
                id="password"
                v-model="form.password"
                type="password"
                autocomplete="current-password"
                required
                class="input-field"
                :class="{ 'border-red-300': errors.password }"
              />
              <p v-if="errors.password" class="mt-1 text-sm text-red-600">
                {{ errors.password }}
              </p>
            </div>
          </div>

          <!-- Submit button -->
          <div>
            <button
              type="submit"
              :disabled="authStore.isLoading"
              class="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="authStore.isLoading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Signing in...
              </span>
              <span v-else>Sign in</span>
            </button>
          </div>
        </form>

        <!-- Register link -->
        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">Don't have an account?</span>
            </div>
          </div>

          <div class="mt-6">
            <router-link
              to="/register"
              class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200"
            >
              Create new account
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { LoginCredentials } from '@/types/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive<LoginCredentials>({
  username_or_email: '',
  password: ''
})

const errors = ref<Record<string, string>>({})

const validateForm = (): boolean => {
  errors.value = {}

  if (!form.username_or_email.trim()) {
    errors.value.username_or_email = 'Username or Email is required'
  }

  if (!form.password) {
    errors.value.password = 'Password is required'
  }

  return Object.keys(errors.value).length === 0
}

const handleLogin = async () => {
  if (!validateForm()) return

  try {
    await authStore.login(form)

    // Redirect to intended page or dashboard
    const redirectTo = route.query.redirect as string || '/dashboard'
    router.push(redirectTo)
  } catch (error: any) {
    console.error('Login failed:', error)

    // Handle field-specific errors
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    }
  }
}

onMounted(() => {
  authStore.clearError()
})
</script>
