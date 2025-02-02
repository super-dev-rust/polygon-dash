import axios from 'axios'
import { appConfig } from '@/utils/config'

const { API_BASE_URL } = appConfig

const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

const ENDPOINTS = {
  FETCH_TABLE: `/dash/miners`,
  FETCH_MINER: (address) => `/dash/miners/${address}`,
  FETCH_MINER_DISTRIBUTION: `/dash/trust-distribution`,
}

export const fetchTable = (args) => apiClient.get(ENDPOINTS.FETCH_TABLE, { params: args })
export const fetchMiner = ({ address, params }) => apiClient.get(ENDPOINTS.FETCH_MINER(address), { params })
export const fetchMinerDistribution = () => apiClient.get(ENDPOINTS.FETCH_MINER_DISTRIBUTION)