import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { debtApi } from "@/services/api";
import type { Debt, DebtCreate, PaginatedResponse } from "@/types/api";

export const useDebtStore = defineStore("debts", () => {
  // State
  const debts = ref<Debt[]>([]);
  const filteredDebts = ref<Debt[]>([]);
  const currentDebt = ref<Debt | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const owedToMe = computed(() =>
    debts.value.filter(
      (debt) => debt.is_owed_to_me && debt.status === "pending",
    ),
  );

  const iOwe = computed(() =>
    debts.value.filter(
      (debt) => !debt.is_owed_to_me && debt.status === "pending",
    ),
  );

  const totalOwedToMe = computed(() =>
    owedToMe.value.reduce((sum, debt) => sum + debt.amount, 0),
  );

  const totalIOwe = computed(() =>
    iOwe.value.reduce((sum, debt) => sum + debt.amount, 0),
  );

  const pendingDebts = computed(() =>
    debts.value.filter((debt) => debt.status === "pending"),
  );

  const overdueDebts = computed(() =>
    debts.value.filter(
      (debt) =>
        debt.status === "pending" && new Date(debt.due_date) < new Date(),
    ),
  );

  // Actions
  const fetchDebts = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await debtApi.getAll();
      debts.value = response.results;
      filteredDebts.value = response.results;
    } catch (err: any) {
      error.value = err.response?.data?.message || "Failed to fetch debts";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const searchDebts = async (search: string) => {
    isLoading.value = true;
    error.value = null;
    try {
      if (!search) {
        // If search is empty, show all debts
        await fetchDebts();
      } else {
        const response = await debtApi.getAllWithSearch(search);
        filteredDebts.value = response.results;
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || "Failed to search debts";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchDebtById = async (id: string) => {
    isLoading.value = true;
    error.value = null;

    try {
      const data = await debtApi.getById(id);
      currentDebt.value = data;
      return data;
    } catch (err: any) {
      error.value = err.response?.data?.message || "Failed to fetch debt";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const createDebt = async (data: DebtCreate) => {
    isLoading.value = true;
    error.value = null;

    try {
      const newDebt = await debtApi.create(data);
      debts.value.push(newDebt);
      return newDebt;
    } catch (err: any) {
      error.value = err.response?.data?.message || "Failed to create debt";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updateDebt = async (id: string, data: Partial<DebtCreate>) => {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedDebt = await debtApi.update(id, data);
      const index = debts.value.findIndex((debt) => debt.id === id);
      if (index !== -1) {
        debts.value[index] = updatedDebt;
      }
      if (currentDebt.value?.id === id) {
        currentDebt.value = updatedDebt;
      }
      return updatedDebt;
    } catch (err: any) {
      error.value = err.response?.data?.message || "Failed to update debt";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteDebt = async (id: string) => {
    isLoading.value = true;
    error.value = null;

    try {
      await debtApi.delete(id);
      debts.value = debts.value.filter((debt) => debt.id !== id);
      if (currentDebt.value?.id === id) {
        currentDebt.value = null;
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || "Failed to delete debt";
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const clearError = () => {
    error.value = null;
  };

  const clearCurrentDebt = () => {
    currentDebt.value = null;
  };

  return {
    // State
    debts,
    filteredDebts,
    currentDebt,
    isLoading,
    error,
    // Getters
    owedToMe,
    iOwe,
    totalOwedToMe,
    totalIOwe,
    pendingDebts,
    overdueDebts,
    // Actions
    fetchDebts,
    searchDebts,
    fetchDebtById,
    createDebt,
    updateDebt,
    deleteDebt,
    clearError,
    clearCurrentDebt,
  };
});
