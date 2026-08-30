import styles from './Stepper.module.css'

const CHECK = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 6L9 17l-5-5" />
  </svg>
)

export default function Stepper({ steps, current }) {
  return (
    <div className={styles.stepper}>
      {steps.map((label, i) => {
        const isDone = i < current
        const isActive = i === current
        return (
          <span key={label} className={styles.stepGroup}>
            {i > 0 && <span className={styles.rule} />}
            <span className={`${styles.step} ${isDone ? styles.stepDone : ''} ${isActive ? styles.stepActive : ''}`}>
              <span className={styles.num}>{isDone ? CHECK : i + 1}</span>
              {label}
            </span>
          </span>
        )
      })}
    </div>
  )
}
