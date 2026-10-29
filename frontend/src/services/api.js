
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://gridbricks-ele-gen.onrender.com',
})

export const getAnalysis = (month = '2026-01', cutoff = '12:00') =>
  api.get('/api/forecast-analysis', {
    params: {
      month,
      cutoff_utc: cutoff,
    },
  })

export const getHistory = (startTime) =>
  api.get('/api/forecast-history', {
    params: {
      start_time: startTime,
    },
  })

export const getHealth = () => api.get('/api/health')
