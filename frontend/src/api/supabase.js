import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://oiraltamwkuourakwzeg.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pcmFsdGFtd2t1b3VyYWt3emVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxMDA5NzgsImV4cCI6MjEwMzY3Njk3OH0.aS0TVWPYUgv7C3T08mmamibZ2d3huqv4XUbuXjSOCnY'

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
