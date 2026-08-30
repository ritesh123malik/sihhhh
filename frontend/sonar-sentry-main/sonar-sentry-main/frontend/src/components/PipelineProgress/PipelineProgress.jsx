import styles from './PipelineProgress.module.css'

function stagesFor(status) {
  if (status === 'done') {
    return [
      { label: 'Preprocessing', meta: 'complete', status: 'done' },
      { label: 'Feature extraction', meta: 'complete', status: 'done' },
      { label: 'Classification', meta: 'complete', status: 'done' },
      { label: 'Report assembly', meta: 'complete', status: 'done' },
    ]
  }
  if (status === 'running') {
    return [
      { label: 'Preprocessing', meta: 'running', status: 'done' },
      { label: 'Feature extraction', meta: 'in progress', status: 'active' },
      { label: 'Classification', meta: 'queued', status: 'pending' },
      { label: 'Report assembly', meta: 'queued', status: 'pending' },
    ]
  }
  if (status === 'error') {
    return [
      { label: 'Preprocessing', meta: 'complete', status: 'done' },
      { label: 'Feature extraction', meta: 'failed', status: 'active' },
      { label: 'Classification', meta: 'stopped', status: 'pending' },
      { label: 'Report assembly', meta: 'stopped', status: 'pending' },
    ]
  }
  return [
    { label: 'Preprocessing', meta: 'waiting', status: 'pending' },
    { label: 'Feature extraction', meta: 'waiting', status: 'pending' },
    { label: 'Classification', meta: 'waiting', status: 'pending' },
    { label: 'Report assembly', meta: 'waiting', status: 'pending' },
  ]
}

export default function PipelineProgress({ status = 'idle', filename }) {
  const stages = stagesFor(status)
  const pct = status === 'done' ? 100 : status === 'running' ? 46 : status === 'error' ? 28 : 0
  const headline =
    status === 'done' ? 'Stage 4 of 4 — Report assembly' :
    status === 'running' ? 'Stage 2 of 4 — Feature extraction' :
    status === 'error' ? 'Pipeline stopped' :
    filename ? `Queued — ${filename}` : 'Waiting for upload'

  return (
    <section className={styles.panel}>
      <div className={styles.panelTitle}>Pipeline progress</div>

      <div className={styles.progressRow}>
        <span className={styles.stageLabel}>{headline}</span>
        <span className={`${styles.pct} tabular`}>{pct}%</span>
      </div>

      <div className={styles.track}>
        <div className={styles.fill} style={{ width: `${pct}%` }} />
      </div>

      <div className={styles.stageList}>
        {stages.map((s) => (
          <div key={s.label} className={`${styles.stageRow} ${s.status === 'done' ? styles.stageRowDone : ''} ${s.status === 'active' ? styles.stageRowActive : ''}`}>
            <span className={`${styles.dot} ${s.status === 'active' ? styles.dotActive : ''} ${s.status === 'done' ? styles.dotDone : ''}`} />
            <span className={styles.stageName}>{s.label}</span>
            <span className={`${styles.stageMeta} tabular`}>{s.meta}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
