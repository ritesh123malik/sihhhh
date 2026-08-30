import styles from './MetadataPanel.module.css'

export default function MetadataPanel({ value, onChange }) {
  function patch(key, next) {
    onChange({ ...value, [key]: next })
  }

  return (
    <section className={styles.panel}>
      <div className={styles.panelTitle}>Scan metadata</div>

      <div className={styles.fieldRow}>
        <div className={styles.field}>
          <label htmlFor="lat">Latitude</label>
          <input
            type="text"
            id="lat"
            value={value.latitude}
            onChange={(e) => patch('latitude', e.target.value)}
            className="tabular"
          />
        </div>
        <div className={styles.field}>
          <label htmlFor="lng">Longitude</label>
          <input
            type="text"
            id="lng"
            value={value.longitude}
            onChange={(e) => patch('longitude', e.target.value)}
            className="tabular"
          />
        </div>
      </div>

      <div className={styles.fieldRow}>
        <div className={styles.field}>
          <label htmlFor="sonar-type">Sonar type</label>
          <select
            id="sonar-type"
            value={value.sonarType}
            onChange={(e) => patch('sonarType', e.target.value)}
          >
            <option>Side-Scan</option>
            <option>Multibeam</option>
            <option>Synthetic Aperture</option>
          </select>
        </div>
        <div className={styles.field}>
          <label htmlFor="resolution">Resolution</label>
          <select
            id="resolution"
            value={value.resolution}
            onChange={(e) => patch('resolution', e.target.value)}
          >
            <option>0.1 m/px</option>
            <option>0.5 m/px</option>
            <option>1 m/px</option>
          </select>
        </div>
      </div>

      <div className={styles.fieldRow}>
        <div className={styles.field}>
          <label htmlFor="depth-min">Depth min (m)</label>
          <input
            type="text"
            id="depth-min"
            value={value.depthMin}
            onChange={(e) => patch('depthMin', e.target.value)}
            className="tabular"
          />
        </div>
        <div className={styles.field}>
          <label htmlFor="depth-max">Depth max (m)</label>
          <input
            type="text"
            id="depth-max"
            value={value.depthMax}
            onChange={(e) => patch('depthMax', e.target.value)}
            className="tabular"
          />
        </div>
      </div>
    </section>
  )
}
