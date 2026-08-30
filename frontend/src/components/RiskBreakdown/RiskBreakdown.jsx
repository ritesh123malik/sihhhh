import styles from './RiskBreakdown.module.css'

export default function RiskBreakdown({ summary = {} }) {
  const high = (summary.high_risk ?? 0) + (summary.critical_risk ?? 0)
  const medium = summary.medium_risk ?? 0
  const low = summary.low_risk ?? 0
  const total = summary.total || high + medium + low || 1
  const segments = [
    { key: 'high', label: 'High', count: high, pct: `${(high / total) * 100}%` },
    { key: 'medium', label: 'Medium', count: medium, pct: `${(medium / total) * 100}%` },
    { key: 'low', label: 'Low', count: low, pct: `${(low / total) * 100}%` },
  ]

  return (
    <div className={styles.riskBarWrap}>
      <div className={styles.riskBarTop}>
        <span className={styles.riskBarTop__label}>Risk breakdown — {summary.total ?? 0} objects</span>
      </div>
      <div
        className={styles.riskBar}
        role="img"
        aria-label={`Risk breakdown: ${high} high, ${medium} medium, ${low} low risk detections`}
      >
        {segments.map((s) => (
          <div
            key={s.key}
            className={`${styles.riskSeg} ${
              s.key === 'high' ? styles.riskSegHigh :
              s.key === 'medium' ? styles.riskSegMedium :
              styles.riskSegLow
            }`}
            style={{ width: s.pct }}
          />
        ))}
      </div>
      <div className={styles.riskLegend}>
        {segments.map((s) => (
          <span key={s.key} className={styles.riskLegend__item}>
            <span className={`${styles.riskLegend__dot} ${
              s.key === 'high' ? styles.riskLegend__dotHigh :
              s.key === 'medium' ? styles.riskLegend__dotMedium :
              styles.riskLegend__dotLow
            }`} />
            {s.label} <span className={`${styles.riskLegend__val} tabular`}>{s.count}</span>
          </span>
        ))}
      </div>
    </div>
  )
}
