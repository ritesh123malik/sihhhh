import styles from './MetadataStrip.module.css'

export default function MetadataStrip({ metadata = {} }) {
  const items = [
    { label: 'Sonar type', value: metadata.sonar_type || '—' },
    { label: 'Resolution', value: metadata.resolution || '—' },
    {
      label: 'Depth range',
      value: metadata.depth_min != null && metadata.depth_max != null
        ? `${metadata.depth_min}–${metadata.depth_max} m`
        : '—',
    },
    { label: 'Coordinates', value: metadata.latitude != null ? `${metadata.latitude}, ${metadata.longitude}` : '—' },
  ]

  return (
    <div className={styles.metaStrip}>
      {items.map((item) => (
        <div key={item.label} className={styles.metaCell}>
          <span className={styles.metaCell__label}>{item.label}</span>
          <span className={`${styles.metaCell__value} tabular`}>{item.value}</span>
        </div>
      ))}
    </div>
  )
}
