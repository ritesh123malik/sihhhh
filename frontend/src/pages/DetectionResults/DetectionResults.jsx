import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import Topbar from '../../components/Topbar/Topbar'
import Breadcrumb from '../../components/Breadcrumb/Breadcrumb'
import PageHeader from '../../components/PageHeader/PageHeader'
import StatusMetrics from '../../components/StatusMetrics/StatusMetrics'
import DetectionSummary from '../../components/DetectionSummary/DetectionSummary'
import AnnotatedScan from '../../components/AnnotatedScan/AnnotatedScan'
import RiskBreakdown from '../../components/RiskBreakdown/RiskBreakdown'
import MetadataStrip from '../../components/MetadataStrip/MetadataStrip'
import DetectionList from '../../components/DetectionList/DetectionList'
import ActionBar from '../../components/ActionBar/ActionBar'
import { createReportInstance, deleteRun, forgetLastScanIfRun, getRun, runFileUrl } from '../../api/client'
import { exportRunCsv } from '../../utils/exportReport'
import styles from './DetectionResults.module.css'

function formatDuration(seconds) {
  if (!seconds && seconds !== 0) return '—'
  if (seconds < 60) return `${Math.round(seconds)}s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return `${m}m ${s}s`
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const mb = bytes / (1024 * 1024)
  if (mb < 1) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${mb.toFixed(1)} MB`
}

function timeAgo(iso) {
  if (!iso) return 'just now'
  const stamp = iso.endsWith('Z') || /[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`
  const delta = Date.now() - new Date(stamp).getTime()
  const mins = Math.max(0, Math.round(delta / 60000))
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.round(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.round(hours / 24)}d ago`
}

function summarize(detections) {
  const total = detections.length
  const high_risk = detections.filter((d) => d.risk_level === 'high').length
  const critical_risk = detections.filter((d) => d.risk_level === 'critical').length
  const medium_risk = detections.filter((d) => d.risk_level === 'medium').length
  const low_risk = detections.filter((d) => d.risk_level === 'low').length
  const avg_confidence = total
    ? detections.reduce((sum, d) => sum + (d.confidence || 0), 0) / total
    : 0
  return { total, high_risk, critical_risk, medium_risk, low_risk, avg_confidence }
}

export default function DetectionResults() {
  const { runId } = useParams()
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const [run, setRun] = useState(null)
  const [error, setError] = useState('')
  const [selectedId, setSelectedId] = useState(null)
  const queryThreshold = Number(params.get('threshold'))
  const [threshold, setThreshold] = useState(
    Number.isFinite(queryThreshold) ? queryThreshold : 0,
  )
  const [instanceNote, setInstanceNote] = useState('')
  const dirty = useRef(false)

  useEffect(() => {
    setError('')
    setSelectedId(null)
    dirty.current = false
    const nextThreshold = Number.isFinite(queryThreshold) ? queryThreshold : 0
    setThreshold(nextThreshold)
    getRun(runId)
      .then((data) => {
        setRun(data)
        const visible = (data.detections || []).filter(
          (d) => Math.round((d.confidence || 0) * 100) >= nextThreshold,
        )
        const first = visible.find((d) => d.bbox) || visible[0]
        if (first) setSelectedId(first.detection_id)
      })
      .catch((err) => setError(err.message || 'Unable to load this run.'))
  }, [runId, queryThreshold])

  useEffect(() => {
    if (!run || !dirty.current) return undefined
    const timer = setTimeout(() => {
      createReportInstance(run.run_id, threshold)
        .then((item) => {
          setInstanceNote(`Saved ${threshold}% instance · ${item.anomaly_count} objects (same scan, not a new upload)`)
        })
        .catch(() => {
          setInstanceNote('Could not save threshold instance.')
        })
    }, 500)
    return () => clearTimeout(timer)
  }, [threshold, run])

  const allDetections = run?.detections || []
  const visibleDetections = useMemo(
    () => allDetections.filter((d) => Math.round((d.confidence || 0) * 100) >= threshold),
    [allDetections, threshold],
  )
  const summary = useMemo(() => summarize(visibleDetections), [visibleDetections])

  useEffect(() => {
    if (!visibleDetections.some((d) => d.detection_id === selectedId)) {
      setSelectedId(visibleDetections[0]?.detection_id || null)
    }
  }, [visibleDetections, selectedId])

  if (error) {
    return (
      <>
        <Topbar activePage="uploads" />
        <PageHeader title="Detection results" description={error} />
      </>
    )
  }

  if (!run) {
    return (
      <>
        <Topbar activePage="uploads" />
        <PageHeader title="Detection results" description="Loading pipeline output…" />
      </>
    )
  }

  const meta = run.scan_metadata || {}
  const avgPct = Math.round((summary.avg_confidence || 0) * 100)
  const durationSeconds =
    run.timestamps?.duration_seconds ??
    (run.created_at && run.updated_at
      ? Math.max(0, (new Date(run.updated_at) - new Date(run.created_at)) / 1000)
      : null)
  const imageUrl = `${runFileUrl(run.run_id)}?inline=1`

  const metrics = [
    { label: 'Run time', value: formatDuration(durationSeconds) },
    { label: 'File size', value: formatBytes(meta.file_size_bytes) },
    { label: 'Avg. confidence', value: `${avgPct}%` },
    { label: 'Pipeline status', value: run.status === 'completed' ? 'Complete' : run.status, ok: run.status === 'completed' },
  ]

  async function handleDelete() {
    if (!window.confirm(`Delete upload ${meta.filename || run.mission_id}? This also removes its reports.`)) {
      return
    }
    await deleteRun(run.run_id)
    forgetLastScanIfRun(run.run_id)
    navigate('/uploads')
  }

  return (
    <>
      <Topbar activePage="uploads" />
      <Breadcrumb filename={meta.filename} onBack={() => navigate('/uploads')} />
      <PageHeader
        title="Detection results"
        description={`${run.mission_id} · ${meta.latitude ?? '—'}, ${meta.longitude ?? '—'} · ${formatBytes(meta.file_size_bytes)} · uploaded ${timeAgo(run.created_at)}`}
      />
      <StatusMetrics items={metrics} />
      <main className={styles.workSurface}>
        <section className={styles.panel}>
          <DetectionSummary summary={summary} />
          <AnnotatedScan
            imageUrl={imageUrl}
            filename={meta.filename}
            detections={visibleDetections}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
          <RiskBreakdown summary={summary} />
          <MetadataStrip metadata={meta} />
        </section>
        <DetectionList
          detections={visibleDetections}
          selectedId={selectedId}
          onSelect={setSelectedId}
          threshold={threshold}
          instanceNote={instanceNote}
          onThresholdChange={(value) => {
            dirty.current = true
            setThreshold(value)
          }}
        />
        <ActionBar
          filename={meta.filename}
          count={summary.total || visibleDetections.length}
          runId={run.run_id}
          onExport={() => exportRunCsv({ ...run, detections: visibleDetections, detection_summary: summary })}
          onDelete={handleDelete}
        />
      </main>
    </>
  )
}
