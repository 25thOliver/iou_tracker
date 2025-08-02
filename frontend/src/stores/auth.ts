import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services/api'
import type { User, LoginCredentials, RegisterData } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const username = computed(() => user.value?.username || '')

  // Actions
  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authApi.login(credentials)
      user.value = response.user
      return response
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = async (data: RegisterData) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authApi.register(data)
      user.value = response.user
      return response
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      await authApi.logout()
      user.value = null
    } catch (err: any) {
      console.error('Logout error:', err)
    } finally {
      isLoading.value = false
    }
  }

  const loadUserFromStorage = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (err) {
        console.error('Error parsing saved user:', err)
        localStorage.removeItem('user')
      }
    }
  }

  const getCurrentUser = async () => {
    if (!isAuthenticated.value) return
    
    isLoading.value = true
    try {
      const userData = await authApi.getCurrentUser()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (err: any) {
      console.error('Error fetching current user:', err)
      if (err.response?.status === 401) {
        user.value = null
        localStorage.removeItem('user')
        localStorage.removeItem('auth_token')
      }
    } finally {
      isLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  // Initialize user from localStorage on store creation
  loadUserFromStorage()

  return {
    // State
    user,
    isLoading,
    error,
    // Getters
    isAuthenticated,
    username,
    // Actions
    login,
    register,
    logout,
    loadUserFromStorage,
    getCurrentUser,
    clearError
  }
})
