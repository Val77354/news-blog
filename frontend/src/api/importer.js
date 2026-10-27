import { apiFetch } from './client'

export const importNews = (options) => apiFetch('/import', { method: 'POST', json: options })
