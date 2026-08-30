import styles from './Breadcrumb.module.css'

export default function Breadcrumb({ filename = 'sonar scan', onBack }) {
  return (
    <section className={styles.crumbRow}>
      <button className={styles.btnBack} type="button" onClick={onBack}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="m12 19l-7-7l7-7m7 7H5" />
        </svg>
        My Uploads
      </button>
      <span className={styles.crumbSep}>/</span>
      <span className={`${styles.crumbFile} tabular`}>{filename}</span>
    </section>
  )
}
