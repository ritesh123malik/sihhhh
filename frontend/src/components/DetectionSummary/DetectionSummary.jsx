import styles from './DetectionSummary.module.css'

export default function DetectionSummary({ summary = {} }) {
  const total = summary.total ?? 0
  const high = (summary.high_risk ?? 0) + (summary.critical_risk ?? 0)
  return (
    <div className={styles.heroStatRow}>
      <div className={styles.heroStat}>
        <span className={styles.heroStat__label}>Total detections</span>
        <span className={`${styles.heroStat__value} tabular`}>{total}</span>
        <span className={styles.heroStat__qualifier}>
          {high} high risk · <span className={styles.delta}>flagged for review</span>
        </span>
      </div>
    </div>
  )
}
