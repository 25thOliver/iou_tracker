<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Profile</h1>
      <p class="mt-1 text-sm text-gray-500">
        Manage your account settings and preferences.
      </p>
    </div>

    <!-- Profile Information -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-6">Profile Information</h3>
        
        <form @submit.prevent="updateProfile" class="space-y-6">
          <!-- Error message -->
          <div
            v-if="error"
            class="rounded-md bg-red-50 p-4 border border-red-200"
          >
            <div class="text-sm text-red-700">
              {{ error }}
            </div>
          </div>

          <!-- Success message -->
          <div
            v-if="successMessage"
            class="rounded-md bg-green-50 p-4 border border-green-200"
          >
            <div class="text-sm text-green-700">
              {{ successMessage }}
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Username -->
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700">
                Username
              </label>
              <div class="mt-1">
                <input
                  id="username"
                  v-model="profileForm.username"
                  type="text"
                  required
                  class="input-field"
                  :class="{ 'border-red-300': errors.username }"
                />
                <p v-if="errors.username" class="mt-1 text-sm text-red-600">
                  {{ errors.username }}
                </p>
              </div>
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">
                Email
              </label>
              <div class="mt-1">
                <input
                  id="email"
                  v-model="profileForm.email"
                  type="email"
                  required
                  class="input-field"
                  :class="{ 'border-red-300': errors.email }"
                />
                <p v-if="errors.email" class="mt-1 text-sm text-red-600">
                  {{ errors.email }}
                </p>
              </div>
            </div>

            <!-- First Name -->
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-700">
                First Name
              </label>
              <div class="mt-1">
                <input
                  id="first_name"
                  v-model="profileForm.first_name"
                  type="text"
                  class="input-field"
                  :class="{ 'border-red-300': errors.first_name }"
                />
                <p v-if="errors.first_name" class="mt-1 text-sm text-red-600">
                  {{ errors.first_name }}
                </p>
              </div>
            </div>

            <!-- Last Name -->
            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-700">
                Last Name
              </label>
              <div class="mt-1">
                <input
                  id="last_name"
                  v-model="profileForm.last_name"
                  type="text"
                  class="input-field"
                  :class="{ 'border-red-300': errors.last_name }"
                />
                <p v-if="errors.last_name" class="mt-1 text-sm text-red-600">
                  {{ errors.last_name }}
                </p>
              </div>
            </div>
          </div>

          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="isUpdating"
              class="btn-primary disabled:opacity-50"
            >
              {{ isUpdating ? 'Updating...' : 'Update Profile' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Account Statistics -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-6">Account Statistics</h3>
        
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-900">{{ stats.totalIOUs }}</p>
            <p class="text-sm text-gray-500">Total IOUs</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-900">{{ stats.totalDebts }}</p>
            <p class="text-sm text-gray-500">Total Debts</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-green-600">{{ formatAmount(stats.totalOwedToMe) }}</p>
            <p class="text-sm text-gray-500">Owed to me</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-red-600">{{ formatAmount(stats.totalIOwe) }}</p>
            <p class="text-sm text-gray-500">I owe</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Account Actions -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-6">Account Actions</h3>
        
        <div class="space-y-4">
          <div class="flex items-center justify-between py-3 border-b border-gray-200">
            <div>
              <h4 class="text-sm font-medium text-gray-900">Change Password</h4>
              <p class="text-sm text-gray-500">Update your account password</p>
            </div>
            <button
              @click="showPasswordForm = !showPasswordForm"
              class="btn-secondary"
            >
              {{ showPasswordForm ? 'Cancel' : 'Change Password' }}
            </button>
          </div>

          <!-- Password change form -->
          <div v-if="showPasswordForm" class="bg-gray-50 rounded-lg p-4">
            <form @submit.prevent="changePassword" class="space-y-4">
              <div>
                <label for="current_password" class="block text-sm font-medium text-gray-700">
                  Current Password
                </label>
                <div class="mt-1">
                  <input
                    id="current_password"
                    v-model="passwordForm.current_password"
                    type="password"
                    required
                    class="input-field"
                    :class="{ 'border-red-300': passwordErrors.current_password }"
                  />
                  <p v-if="passwordErrors.current_password" class="mt-1 text-sm text-red-600">
                    {{ passwordErrors.current_password }}
                  </p>
                </div>
              </div>

              <div>
                <label for="new_password" class="block text-sm font-medium text-gray-700">
                  New Password
                </label>
                <div class="mt-1">
                  <input
                    id="new_password"
                    v-model="passwordForm.new_password"
                    type="password"
                    required
                    class="input-field"
                    :class="{ 'border-red-300': passwordErrors.new_password }"
                  />
                  <p v-if="passwordErrors.new_password" class="mt-1 text-sm text-red-600">
                    {{ passwordErrors.new_password }}
                  </p>
                </div>
              </div>

              <div>
                <label for="confirm_password" class="block text-sm font-medium text-gray-700">
                  Confirm New Password
                </label>
                <div class="mt-1">
                  <input
                    id="confirm_password"
                    v-model="passwordForm.confirm_password"
                    type="password"
                    required
                    class="input-field"
                    :class="{ 'border-red-300': passwordErrors.confirm_password }"
                  />
                  <p v-if="passwordErrors.confirm_password" class="mt-1 text-sm text-red-600">
                    {{ passwordErrors.confirm_password }}
                  </p>
                </div>
              </div>

              <div class="flex justify-end space-x-3">
                <button
                  type="button"
                  @click="showPasswordForm = false"
                  class="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="isChangingPassword"
                  class="btn-primary disabled:opacity-50"
                >
                  {{ isChangingPassword ? 'Changing...' : 'Change Password' }}
                </button>
              </div>
            </form>
          </div>

          <div class="flex items-center justify-between py-3">
            <div>
              <h4 class="text-sm font-medium text-gray-900">Logout</h4>
              <p class="text-sm text-gray-500">Sign out of your account</p>
            </div>
            <button
              @click="handleLogout"
              class="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useIOUStore } from '@/stores/ious'
import { useDebtStore } from '@/stores/debts'

const router = useRouter()
const authStore = useAuthStore()
const iouStore = useIOUStore()
const debtStore = useDebtStore()

const profileForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: ''
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const errors = ref<Record<string, string>>({})
const passwordErrors = ref<Record<string, string>>({})
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const isUpdating = ref(false)
const isChangingPassword = ref(false)
const showPasswordForm = ref(false)

const stats = computed(() => ({
  totalIOUs: iouStore.ious.length,
  totalDebts: debtStore.debts.length,
  totalOwedToMe: iouStore.totalOwedToMe + debtStore.totalOwedToMe,
  totalIOwe: iouStore.totalIOwe + debtStore.totalIOwe
}))

const formatAmount = (amount: number): string => {
  return amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const validateProfileForm = (): boolean => {
  errors.value = {}
  
  if (!profileForm.username.trim()) {
    errors.value.username = 'Username is required'
  }
  
  if (!profileForm.email.trim()) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileForm.email)) {
    errors.value.email = 'Please enter a valid email address'
  }
  
  return Object.keys(errors.value).length === 0
}

const validatePasswordForm = (): boolean => {
  passwordErrors.value = {}
  
  if (!passwordForm.current_password) {
    passwordErrors.value.current_password = 'Current password is required'
  }
  
  if (!passwordForm.new_password) {
    passwordErrors.value.new_password = 'New password is required'
  } else if (passwordForm.new_password.length < 8) {
    passwordErrors.value.new_password = 'Password must be at least 8 characters'
  }
  
  if (!passwordForm.confirm_password) {
    passwordErrors.value.confirm_password = 'Please confirm your new password'
  } else if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordErrors.value.confirm_password = 'Passwords do not match'
  }
  
  return Object.keys(passwordErrors.value).length === 0
}

const updateProfile = async () => {
  if (!validateProfileForm()) return
  
  isUpdating.value = true
  error.value = null
  successMessage.value = null
  
  try {
    // This would be implemented with a real API call
    console.log('Update profile:', profileForm)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    successMessage.value = 'Profile updated successfully!'
    
    // Hide success message after 3 seconds
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (err: any) {
    console.error('Error updating profile:', err)
    error.value = 'Failed to update profile'
  } finally {
    isUpdating.value = false
  }
}

const changePassword = async () => {
  if (!validatePasswordForm()) return
  
  isChangingPassword.value = true
  error.value = null
  successMessage.value = null
  
  try {
    // This would be implemented with a real API call
    console.log('Change password')
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    successMessage.value = 'Password changed successfully!'
    showPasswordForm.value = false
    
    // Reset password form
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    
    // Hide success message after 3 seconds
    setTimeout(() => {
      successMessage.value = null
    }, 3000)
  } catch (err: any) {
    console.error('Error changing password:', err)
    error.value = 'Failed to change password'
  } finally {
    isChangingPassword.value = false
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

onMounted(async () => {
  // Load user data into form
  if (authStore.user) {
    profileForm.username = authStore.user.username || ''
    profileForm.email = authStore.user.email || ''
    profileForm.first_name = authStore.user.first_name || ''
    profileForm.last_name = authStore.user.last_name || ''
  }

  // Load statistics data
  try {
    await Promise.all([
      iouStore.fetchIOUs(),
      debtStore.fetchDebts()
    ])
  } catch (error) {
    console.error('Error loading statistics:', error)
  }
})
</script>
