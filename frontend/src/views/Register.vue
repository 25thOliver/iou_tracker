<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-900">IOU Tracker</h1>
        <h2 class="mt-6 text-2xl font-medium text-gray-900">
          Create your account
        </h2>
      </div>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form @submit.prevent="handleRegister" class="space-y-6">
          <!-- Error message -->
          <div
            v-if="authStore.error"
            class="rounded-md bg-red-50 p-4 border border-red-200"
          >
            <div class="text-sm text-red-700">
              {{ authStore.error }}
            </div>
          </div>

          <!-- Username field -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              Username
            </label>
            <div class="mt-1">
              <input
                id="username"
                v-model="form.username"
                type="text"
                autocomplete="username"
                required
                class="input-field"
                :class="{ 'border-red-300': errors.username }"
              />
              <p v-if="errors.username" class="mt-1 text-sm text-red-600">
                {{ errors.username }}
              </p>
            </div>
          </div>

          <!-- Email field -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email address
            </label>
            <div class="mt-1">
              <input
                id="email"
                v-model="form.email"
                type="email"
                autocomplete="email"
                required
                class="input-field"
                :class="{ 'border-red-300': errors.email }"
              />
              <p v-if="errors.email" class="mt-1 text-sm text-red-600">
                {{ errors.email }}
              </p>
            </div>
          </div>

          <!-- First name field -->
          <div>
            <label for="first_name" class="block text-sm font-medium text-gray-700">
              First name (optional)
            </label>
            <div class="mt-1">
              <input
                id="first_name"
                v-model="form.first_name"
                type="text"
                autocomplete="given-name"
                class="input-field"
                :class="{ 'border-red-300': errors.first_name }"
              />
              <p v-if="errors.first_name" class="mt-1 text-sm text-red-600">
                {{ errors.first_name }}
              </p>
            </div>
          </div>

          <!-- Last name field -->
          <div>
            <label for="last_name" class="block text-sm font-medium text-gray-700">
              Last name (optional)
            </label>
            <div class="mt-1">
              <input
                id="last_name"
                v-model="form.last_name"
                type="text"
                autocomplete="family-name"
                class="input-field"
                :class="{ 'border-red-300': errors.last_name }"
              />
              <p v-if="errors.last_name" class="mt-1 text-sm text-red-600">
                {{ errors.last_name }}
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
                autocomplete="new-password"
                required
                class="input-field"
                :class="{ 'border-red-300': errors.password }"
              />
              <p v-if="errors.password" class="mt-1 text-sm text-red-600">
                {{ errors.password }}
              </p>
            </div>
          </div>

          <!-- Confirm password field -->
          <div>
            <label for="password_confirm" class="block text-sm font-medium text-gray-700">
              Confirm password
            </label>
            <div class="mt-1">
              <input
                id="password_confirm"
                v-model="form.password_confirm"
                type="password"
                autocomplete="new-password"
                required
                class="input-field"
                :class="{ 'border-red-300': errors.password_confirm }"
              />
              <p v-if="errors.password_confirm" class="mt-1 text-sm text-red-600">
                {{ errors.password_confirm }}
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
                Creating account...
              </span>
              <span v-else>Create account</span>
            </button>
          </div>
        </form>

        <!-- Login link -->
        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">Already have an account?</span>
            </div>
          </div>

          <div class="mt-6">
            <router-link
              to="/login"
              class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200"
            >
              Sign in to existing account
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RegisterData } from '@/types/api'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive<RegisterData>({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: ''
})

const errors = ref<Record<string, string>>({})

const validateForm = (): boolean => {
  errors.value = {}
  
  if (!form.username.trim()) {
    errors.value.username = 'Username is required'
  } else if (form.username.length < 3) {
    errors.value.username = 'Username must be at least 3 characters'
  }
  
  if (!form.email.trim()) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.value.email = 'Please enter a valid email address'
  }
  
  if (!form.password) {
    errors.value.password = 'Password is required'
  } else if (form.password.length < 8) {
    errors.value.password = 'Password must be at least 8 characters'
  }
  
  if (!form.password_confirm) {
    errors.value.password_confirm = 'Please confirm your password'
  } else if (form.password !== form.password_confirm) {
    errors.value.password_confirm = 'Passwords do not match'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleRegister = async () => {
  if (!validateForm()) return
  
  try {
    await authStore.register(form)
    router.push('/dashboard')
  } catch (error: any) {
    console.error('Registration failed:', error)
    
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
