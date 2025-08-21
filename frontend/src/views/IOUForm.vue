<template>
  <div class="max-w-2xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">
        {{ isEdit ? 'Edit IOU' : 'Create New IOU' }}
      </h1>
      <p class="mt-1 text-sm text-gray-500">
        {{ isEdit ? 'Update the details of your IOU.' : 'Fill in the details to create a new IOU.' }}
      </p>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
      <form @submit.prevent="handleSubmit" class="space-y-6 p-6">
        <!-- Error message -->
        <div
          v-if="error"
          class="rounded-md bg-red-50 p-4 border border-red-200"
        >
          <div class="text-sm text-red-700">
            {{ error }}
          </div>
        </div>

        <!-- Description -->
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700">
            Description *
          </label>
          <div class="mt-1">
            <input
              id="description"
              v-model="form.description"
              type="text"
              required
              placeholder="e.g., Lunch money, Loan for car repair"
              class="input-field"
              :class="{ 'border-red-300': errors.description }"
            />
            <p v-if="errors.description" class="mt-1 text-sm text-red-600">
              {{ errors.description }}
            </p>
          </div>
        </div>

        <!-- Amount -->
        <div>
          <label for="amount" class="block text-sm font-medium text-gray-700">
            Amount (KES) *
          </label>
          <div class="mt-1">
            <input
              id="amount"
              v-model.number="form.amount"
              type="number"
              step="0.01"
              min="0"
              required
              placeholder="0.00"
              class="input-field"
              :class="{ 'border-red-300': errors.amount }"
            />
            <p v-if="errors.amount" class="mt-1 text-sm text-red-600">
              {{ errors.amount }}
            </p>
          </div>
        </div>

        <!-- Currency -->
        <div>
          <label for="currency" class="block text-sm font-medium text-gray-700">
            Currency *
          </label>
          <div class="mt-1">
            <select
              id="currency"
              v-model="form.currency"
              required
              class="input-field"
              :class="{ 'border-red-300': errors.currency }"
            >
              <option value="KES">KES (Kenyan Shilling)</option>
              <option value="USD">USD (US Dollar)</option>
              <option value="EUR">EUR (Euro)</option>
              <option value="GBP">GBP (British Pound)</option>
            </select>
            <p v-if="errors.currency" class="mt-1 text-sm text-red-600">
              {{ errors.currency }}
            </p>
          </div>
        </div>

        <!-- Who owes whom -->
        <div class="space-y-4">
          <!-- IOU Type Toggle -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center space-x-4">
              <label class="flex items-center">
                <input
                  v-model="iouType"
                  type="radio"
                  value="lending"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm font-medium text-gray-700">I'm lending money</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="iouType"
                  type="radio"
                  value="borrowing"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span class="ml-2 text-sm font-medium text-gray-700">I'm borrowing money</span>
              </label>
            </div>
          </div>

          <!-- Dynamic form based on IOU type -->
          <div v-if="iouType === 'lending'" class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Debtor (who owes money) -->
            <div>
              <label for="debtor" class="block text-sm font-medium text-gray-700">
                Who owes me money? *
              </label>
              <div class="mt-1">
                <input
                  id="debtor"
                  v-model="form.debtor"
                  type="text"
                  required
                  placeholder="Name of person who owes you"
                  class="input-field"
                  :class="{ 'border-red-300': errors.debtor }"
                />
                <p v-if="errors.debtor" class="mt-1 text-sm text-red-600">
                  {{ errors.debtor }}
                </p>
              </div>
            </div>

            <!-- Creditor (you) - auto-filled -->
            <div>
              <label for="creditor" class="block text-sm font-medium text-gray-700">
                Who is owed money? *
              </label>
              <div class="mt-1">
                <input
                  id="creditor"
                  v-model="form.creditor"
                  type="text"
                  required
                  readonly
                  class="input-field bg-gray-100 cursor-not-allowed"
                  :class="{ 'border-red-300': errors.creditor }"
                />
                <p class="mt-1 text-xs text-gray-500">This is you (auto-filled)</p>
                <p v-if="errors.creditor" class="mt-1 text-sm text-red-600">
                  {{ errors.creditor }}
                </p>
              </div>
            </div>
          </div>

          <div v-else-if="iouType === 'borrowing'" class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Debtor (you) - auto-filled -->
            <div>
              <label for="debtor" class="block text-sm font-medium text-gray-700">
                Who owes money? *
              </label>
              <div class="mt-1">
                <input
                  id="debtor"
                  v-model="form.debtor"
                  type="text"
                  required
                  readonly
                  class="input-field bg-gray-100 cursor-not-allowed"
                  :class="{ 'border-red-300': errors.debtor }"
                />
                <p class="mt-1 text-xs text-gray-500">This is you (auto-filled)</p>
                <p v-if="errors.debtor" class="mt-1 text-sm text-red-600">
                  {{ errors.debtor }}
                </p>
              </div>
            </div>

            <!-- Creditor (who you owe) -->
            <div>
              <label for="creditor" class="block text-sm font-medium text-gray-700">
                Who are you paying back? *
              </label>
              <div class="mt-1">
                <input
                  id="creditor"
                  v-model="form.creditor"
                  type="text"
                  required
                  placeholder="Name of person you owe"
                  class="input-field"
                  :class="{ 'border-red-300': errors.creditor }"
                />
                <p v-if="errors.creditor" class="mt-1 text-sm text-red-600">
                  {{ errors.creditor }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Due date -->
        <div>
          <label for="due_date" class="block text-sm font-medium text-gray-700">
            Due Date *
          </label>
          <div class="mt-1">
            <input
              id="due_date"
              v-model="form.due_date"
              type="date"
              required
              class="input-field"
              :class="{ 'border-red-300': errors.due_date }"
            />
            <p v-if="errors.due_date" class="mt-1 text-sm text-red-600">
              {{ errors.due_date }}
            </p>
          </div>
        </div>

        <!-- Helper text -->
        <div class="bg-blue-50 rounded-lg p-4">
          <div class="flex">
            <InformationCircleIcon class="h-5 w-5 text-blue-400 mt-0.5" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800">
                How IOUs work
              </h3>
              <div class="mt-2 text-sm text-blue-700">
                <p v-if="iouType === 'lending'">
                  <strong>Lending money:</strong> You're the creditor (being owed money). 
                  The debtor is the person who owes you money and will pay you back.
                </p>
                <p v-else>
                  <strong>Borrowing money:</strong> You're the debtor (owing money). 
                  The creditor is the person you owe money to and will pay back.
                </p>
                <p class="mt-2">
                  Choose the scenario above and fill in the details. The form will automatically 
                  fill in your name in the appropriate field.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end space-x-3 pt-6">
          <router-link
            to="/ious"
            class="btn-secondary"
          >
            Cancel
          </router-link>
          <button
            type="submit"
            :disabled="isLoading"
            class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isEdit ? 'Updating...' : 'Creating...' }}
            </span>
            <span v-else>
              {{ isEdit ? 'Update IOU' : 'Create IOU' }}
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { InformationCircleIcon } from '@heroicons/vue/24/outline'
import { useIOUStore } from '@/stores/ious'
import type { IOUCreate } from '@/types/api'
import { useAuthStore } from '@/stores/auth'

interface Props {
  id?: string
}

const props = defineProps<Props>()

const router = useRouter()
const route = useRoute()
const iouStore = useIOUStore()
const authStore = useAuthStore()

const isEdit = computed(() => !!props.id || !!route.params.id)
const iouId = computed(() => props.id || route.params.id as string)

const form = reactive<IOUCreate>({
  description: '',
  amount: 0,
  debtor: '',
  creditor: '',
  due_date: '',
  currency: 'KES' // Add currency field
})

const errors = ref<Record<string, string>>({})
const error = ref<string | null>(null)
const isLoading = ref(false)

const iouType = ref<'lending' | 'borrowing'>('lending')

// Watch for changes in IOU type to auto-populate fields
const updateFormFields = () => {
  if (iouType.value === 'lending') {
    // User is lending money (they are the creditor)
    form.creditor = authStore.username || ''
    form.debtor = '' // Clear debtor field for user input
  } else {
    // User is borrowing money (they are the debtor)
    form.debtor = authStore.username || ''
    form.creditor = '' // Clear creditor field for user input
  }
}

// Watch for IOU type changes
watch(iouType, updateFormFields)

const validateForm = (): boolean => {
  errors.value = {}
  
  if (!form.description.trim()) {
    errors.value.description = 'Description is required'
  }
  
  if (!form.amount || form.amount <= 0) {
    errors.value.amount = 'Amount must be greater than 0'
  }
  
  if (!form.currency) {
    errors.value.currency = 'Currency is required'
  }

  if (!form.debtor.trim()) {
    errors.value.debtor = 'Debtor name is required'
  }
  
  if (!form.creditor.trim()) {
    errors.value.creditor = 'Creditor name is required'
  }
  
  if (!form.due_date) {
    errors.value.due_date = 'Due date is required'
  } else {
    const dueDate = new Date(form.due_date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    if (dueDate < today) {
      errors.value.due_date = 'Due date cannot be in the past'
    }
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isLoading.value = true
  error.value = null
  
  try {
    if (isEdit.value) {
      await iouStore.updateIOU(iouId.value as string, form)
    } else {
      await iouStore.createIOU(form)
    }
    
    router.push('/ious')
  } catch (err: any) {
    console.error('Error saving IOU:', err)
    error.value = err.response?.data?.message || `Failed to ${isEdit.value ? 'update' : 'create'} IOU`
    
    // Handle field-specific errors
    if (err.response?.data?.errors) {
      errors.value = err.response.data.errors
    }
  } finally {
    isLoading.value = false
  }
}

const loadIOUForEdit = async () => {
  if (!isEdit.value) return
  
  try {
    const iou = await iouStore.fetchIOUById(iouId.value as string)
    if (iou) {
      form.description = iou.description
      form.amount = iou.amount
      form.currency = iou.currency
      form.debtor = iou.debtor
      form.creditor = iou.creditor
      form.due_date = iou.due_date.split('T')[0] // Convert to YYYY-MM-DD format
    }
  } catch (err: any) {
    console.error('Error loading IOU:', err)
    error.value = 'Failed to load IOU data'
  }
}

onMounted(() => {
  // Set default due date to tomorrow
  if (!isEdit.value) {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    form.due_date = tomorrow.toISOString().split('T')[0]
    
    // Initialize form fields based on IOU type
    updateFormFields()
  } else {
    loadIOUForEdit()
  }
})
</script>
