import styles from './LaunchBar.module.css'

export default function LaunchBar({ ready, running, onLaunch, instanceOnly = false, threshold = 20 }) {
  const label = running
    ? (instanceOnly ? 'Saving threshold instance…' : 'Running detection…')
    : ready
      ? (instanceOnly
        ? `Only threshold changed — ${threshold}% instance of the last scan`
        : 'Ready to launch')
      : 'Upload a sonar file to continue'

  return (
    <section className={styles.launchBar}>
      <div className={styles.info}>
        <strong>{label}</strong>
      </div>
      <button
        className={styles.btnPrimary}
        type="button"
        disabled={!ready || running}
        onClick={onLaunch}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
          <path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z" />
        </svg>
        {running
          ? 'Processing'
          : instanceOnly
            ? 'Save threshold instance'
            : 'Start AI Detection Pipeline'}
      </button>
    </section>
  )
}
