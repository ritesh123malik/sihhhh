import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Topbar from '../../components/Topbar/Topbar'
import PageHeader from '../../components/PageHeader/PageHeader'
import StatusMetrics from '../../components/StatusMetrics/StatusMetrics'
import { listRuns, deleteRun, forgetLastScanIfRun } from '../../api/client'
import styles from './Uploads.module.css'

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const mb = bytes / (1024 * 1024)
  if (mb < 1) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${mb.toFixed(1)} MB`
}

function formatWhen(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

export default function Uploads() {
  const navigate = useNavigate()
  const [runs, setRuns] = useState([])
  const [error, setError] = useState('')
  const [selectedIds, setSelectedIds] = useState(new Set())

  function loadRuns() {
    listRuns({ pageSize: 100 })
      .then((data) => {
        setRuns(data.items || [])
        // Clean up selected items that no longer exist
        setSelectedIds(prev => {
          const next = new Set(prev)
          const runIds = new Set((data.items || []).map(r => r.run_id))
          for (const id of next) {
            if (!runIds.has(id)) next.delete(id)
          }
          return next
        })
      })
      .catch((err) => setError(err.message || 'Unable to load uploads.'))
  }

  useEffect(() => {
    loadRuns()
  }, [])

  async function handleDelete(event, run) {
    event.stopPropagation()
    if (!window.confirm(`Delete ${run.filename || run.mission_id}? This also removes its reports.`)) {
      return
    }
    await deleteRun(run.run_id)
    forgetLastScanIfRun(run.run_id)
    loadRuns()
  }

  async function handleBulkDelete() {
    if (selectedIds.size === 0) return
    if (!window.confirm(`Delete ${selectedIds.size} selected upload(s)? This also removes their reports.`)) {
      return
    }
    await Promise.all(Array.from(selectedIds).map(async (id) => {
      await deleteRun(id)
      forgetLastScanIfRun(id)
    }))
    setSelectedIds(new Set())
    loadRuns()
  }

  const allSelected = runs.length > 0 && selectedIds.size === runs.length
  function toggleAll() {
    if (allSelected) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(runs.map(r => r.run_id)))
    }
  }

  function toggleOne(event, runId) {
    event.stopPropagation()
    const next = new Set(selectedIds)
    if (next.has(runId)) next.delete(runId)
    else next.add(runId)
    setSelectedIds(next)
  }

  const metrics = [
    { label: 'Total runs', value: String(runs.length) },
    { label: 'Completed', value: String(runs.filter((r) => r.status === 'completed').length), ok: true },
    { label: 'Failed', value: String(runs.filter((r) => r.status === 'failed').length) },
    { label: 'Detections', value: String(runs.reduce((sum, r) => sum + (r.detection_count || 0), 0)) },
  ]

  return (
    <>
      <Topbar activePage="uploads" />
      <PageHeader
        title="My uploads"
        description="Every detection run stored by the local SONARIS backend."
      />
      <StatusMetrics items={metrics} />
      <main className={styles.wrap}>
        {error ? <p className={styles.empty}>{error}</p> : null}
        {!error && runs.length === 0 ? (
          <p className={styles.empty}>No scans yet. Launch a detection run to populate this list.</p>
        ) : (
          <div className={styles.tableContainer}>
            {selectedIds.size > 0 && (
              <div style={{ marginBottom: '1rem', display: 'flex', gap: '1rem' }}>
                <button type="button" className={styles.deleteBtn} onClick={handleBulkDelete}>
                  Delete {selectedIds.size} selected
                </button>
              </div>
            )}
            <div className={styles.tableWrap}>
              <table>
                <thead>
                  <tr>
                    <th style={{ width: '40px', textAlign: 'center' }}>
                      <input 
                        type="checkbox" 
                        checked={allSelected} 
                        onChange={toggleAll}
                        aria-label="Select all"
                      />
                    </th>
                    <th>Mission</th>
                    <th>File</th>
                    <th>Status</th>
                    <th>Detections</th>
                    <th>Size</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((run) => (
                    <tr key={run.run_id} onClick={() => navigate(`/results/${run.run_id}`)}>
                      <td style={{ textAlign: 'center' }} onClick={e => e.stopPropagation()}>
                        <input 
                          type="checkbox" 
                          checked={selectedIds.has(run.run_id)} 
                          onChange={(e) => toggleOne(e, run.run_id)}
                          aria-label={`Select ${run.mission_id}`}
                        />
                      </td>
                      <td className={styles.mission}>{run.mission_id}</td>
                      <td>{run.filename}</td>
                      <td className={styles.status}>{run.status}</td>
                      <td>{run.detection_count}</td>
                      <td>{formatBytes(run.file_size_bytes)}</td>
                      <td>{formatWhen(run.created_at)}</td>
                      <td>
                        <button
                          type="button"
                          className={styles.deleteBtn}
                          onClick={(event) => handleDelete(event, run)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </>
  )
}
