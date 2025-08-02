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
            Amount ($) *
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

        <!-- Who owes whom -->
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <!-- Debtor -->
          <div>
            <label for="debtor" class="block text-sm font-medium text-gray-700">
              Debtor (who owes money) *
            </label>
            <div class="mt-1">
              <input
                id="debtor"
                v-model="form.debtor"
                type="text"
                required
                placeholder="Name of person who owes"
                class="input-field"
                :class="{ 'border-red-300': errors.debtor }"
              />
              <p v-if="errors.debtor" class="mt-1 text-sm text-red-600">
                {{ errors.debtor }}
              </p>
            </div>
          </div>

          <!-- Creditor -->
          <div>
            <label for="creditor" class="block text-sm font-medium text-gray-700">
              Creditor (who is owed money) *
            </label>
            <div class="mt-1">
              <input
                id="creditor"
                v-model="form.creditor"
                type="text"
                required
                placeholder="Name of person who is owed"
                class="input-field"
                :class="{ 'border-red-300': errors.creditor }"
              />
              <p v-if="errors.creditor" class="mt-1 text-sm text-red-600">
                {{ errors.creditor }}
              </p>
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
                Quick tip
              </h3>
              <div class="mt-2 text-sm text-blue-700">
                <p>
                  Make sure to fill in the correct names for debtor and creditor. 
                  This helps keep track of who owes money to whom.
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
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { InformationCircleIcon } from '@heroicons/vue/24/outline'
import { useIOUStore } from '@/stores/ious'
import type { IOUCreate } from '@/types/api'

interface Props {
  id?: string
}

const props = defineProps<Props>()

const router = useRouter()
const route = useRoute()
const iouStore = useIOUStore()

const isEdit = computed(() => !!props.id || !!route.params.id)
const iouId = computed(() => props.id || route.params.id as string)

const form = reactive<IOUCreate>({
  description: '',
  amount: 0,
  debtor: '',
  creditor: '',
  due_date: ''
})

const errors = ref<Record<string, string>>({})
const error = ref<string | null>(null)
const isLoading = ref(false)

const validateForm = (): boolean => {
  errors.value = {}
  
  if (!form.description.trim()) {
    errors.value.description = 'Description is required'
  }
  
  if (!form.amount || form.amount <= 0) {
    errors.value.amount = 'Amount must be greater than 0'
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
      await iouStore.updateIOU(parseInt(iouId.value), form)
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
    const iou = await iouStore.fetchIOUById(parseInt(iouId.value))
    if (iou) {
      form.description = iou.description
      form.amount = iou.amount
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
  } else {
    loadIOUForEdit()
  }
})
</script>
