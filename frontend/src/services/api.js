import axios from 'axios'
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000' })
export const getAnalysis = (month = '2026-01', cutoff = '12:00') => api.get(`/api/forecast-analysis?month=${month}&cutoff_utc=${cutoff}`)
export const getHistory = (startTime) => api.get(`/api/forecast-history?start_time=${encodeURIComponent(startTime)}`)

