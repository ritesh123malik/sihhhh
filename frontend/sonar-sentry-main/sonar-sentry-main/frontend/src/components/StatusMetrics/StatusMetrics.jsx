import styles from './StatusMetrics.module.css'

export default function StatusMetrics({ items }) {
  return (
    <section className={styles.statusRow}>
      {items.map((m) => (
        <div key={m.label} className={styles.statusItem}>
          <span className={styles.statusItem__label}>{m.label}</span>
          <span className={`${styles.statusItem__value} tabular ${m.ok ? styles.statusItem__valueOk : ''}`}>
            {m.value}
          </span>
        </div>
      ))}
    </section>
  )
}
