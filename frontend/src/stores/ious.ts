import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { iouApi } from '@/services/api'
import type { IOU, IOUCreate } from '@/types/api'

export const useIOUStore = defineStore('ious', () => {
  // State
  const ious = ref<IOU[]>([])
  const currentIOU = ref<IOU | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const owedToMe = computed(() => 
    ious.value.filter(iou => iou.is_owed_to_me && iou.status === 'pending')
  )
  
  const iOwe = computed(() => 
    ious.value.filter(iou => !iou.is_owed_to_me && iou.status === 'pending')
  )
  
  const totalOwedToMe = computed(() => 
    owedToMe.value.reduce((sum, iou) => sum + iou.amount, 0)
  )
  
  const totalIOwe = computed(() => 
    iOwe.value.reduce((sum, iou) => sum + iou.amount, 0)
  )

  const pendingIOUs = computed(() => 
    ious.value.filter(iou => iou.status === 'pending')
  )

  const overdueIOUs = computed(() => 
    ious.value.filter(iou => 
      iou.status === 'pending' && new Date(iou.due_date) < new Date()
    )
  )

  // Actions
  const fetchIOUs = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      const data = await iouApi.getAll()
      ious.value = data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch IOUs'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchIOUById = async (id: number) => {
    isLoading.value = true
    error.value = null
    
    try {
      const data = await iouApi.getById(id)
      currentIOU.value = data
      return data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch IOU'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createIOU = async (data: IOUCreate) => {
    isLoading.value = true
    error.value = null
    
    try {
      const newIOU = await iouApi.create(data)
      ious.value.push(newIOU)
      return newIOU
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to create IOU'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateIOU = async (id: number, data: Partial<IOUCreate>) => {
    isLoading.value = true
    error.value = null
    
    try {
      const updatedIOU = await iouApi.update(id, data)
      const index = ious.value.findIndex(iou => iou.id === id)
      if (index !== -1) {
        ious.value[index] = updatedIOU
      }
      if (currentIOU.value?.id === id) {
        currentIOU.value = updatedIOU
      }
      return updatedIOU
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update IOU'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteIOU = async (id: number) => {
    isLoading.value = true
    error.value = null
    
    try {
      await iouApi.delete(id)
      ious.value = ious.value.filter(iou => iou.id !== id)
      if (currentIOU.value?.id === id) {
        currentIOU.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete IOU'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  const clearCurrentIOU = () => {
    currentIOU.value = null
  }

  return {
    // State
    ious,
    currentIOU,
    isLoading,
    error,
    // Getters
    owedToMe,
    iOwe,
    totalOwedToMe,
    totalIOwe,
    pendingIOUs,
    overdueIOUs,
    // Actions
    fetchIOUs,
    fetchIOUById,
    createIOU,
    updateIOU,
    deleteIOU,
    clearError,
    clearCurrentIOU
  }
})
