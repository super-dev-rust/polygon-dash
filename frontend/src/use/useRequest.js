import { ref } from 'vue'

export const useRequest = (request) => {
  const isLoading = ref(false)
  const error = ref(null)
  const data = ref(null)

  const sendRequest = async (args) => {
    isLoading.value = true
    error.value = null
    data.value = null
    try {
      const response = await request(...(args || []))
      data.value = response.data
    } catch (e) {
      error.value = e
    } finally {
      isLoading.value = false
    }
  }

  return {
    sendRequest,
    isLoading,
    error,
    data,
  }
}
