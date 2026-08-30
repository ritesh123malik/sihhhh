import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

export const supabase = supabaseUrl && supabaseAnonKey
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null

export function subscribeToRealtimeDetections(onNewDetection) {
  if (!supabase) return () => {}

  const channel = supabase
    .channel('public:detections')
    .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'detections' }, (payload) => {
      if (onNewDetection) onNewDetection(payload.new)
    })
    .subscribe()

  return () => {
    supabase.removeChannel(channel)
  }
}
