import styles from './PageHeader.module.css'

export default function PageHeader({ title, description }) {
  return (
    <section className={styles.headerBand}>
      <h1>{title}</h1>
      <p>{description}</p>
    </section>
  )
}
