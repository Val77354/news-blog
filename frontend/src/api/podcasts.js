import { apiFetch, withQuery } from './client'

export const listPodcasts = ({ q } = {}) => apiFetch(withQuery('/podcasts', { q }))
export const getPodcast = (id) => apiFetch(`/podcasts/${id}`)
export const createPodcast = (podcast) => apiFetch('/podcasts', { method: 'POST', json: podcast })
export const updatePodcast = (id, podcast) => apiFetch(`/podcasts/${id}`, { method: 'PUT', json: podcast })
export const deletePodcast = (id) => apiFetch(`/podcasts/${id}`, { method: 'DELETE' })
