import { useRef } from 'react'
import styles from './UploadPanel.module.css'

const ACCEPT = '.tif,.tiff,.png,.jpg,.jpeg,.geotiff,image/tiff,image/png,image/jpeg'

export default function UploadPanel({ file, previewUrl, onFile }) {
  const inputRef = useRef(null)

  function takeFile(next) {
    if (!next) return
    onFile(next)
  }

  function onDrop(event) {
    event.preventDefault()
    takeFile(event.dataTransfer.files?.[0])
  }

  return (
    <section className={styles.panel}>
      <div>
        <div className={styles.panelTitle}>SONAR IMAGE UPLOAD SECTION</div>
        <div className={styles.panelSub}>.tiff · .geotiff · .png · .jpg — up to 500MB</div>
      </div>
      <label
        className={styles.dropzone}
        tabIndex={0}
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
      >
        {previewUrl ? (
          <div className={styles.thumbWrap}>
            <img src={previewUrl} alt={file?.name || 'Uploaded sonar image preview'} />
          </div>
        ) : null}
        <div className={styles.icon}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="24" height="24">
            <path d="M12 13v8m-8-6.101A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
            <path d="m8 17l4-4l4 4" />
          </svg>
        </div>
        <h2 className={styles.headline}>{file ? file.name : 'Drop sonar file here'}</h2>
        <span className={styles.meta}>
          {file
            ? `${(file.size / (1024 * 1024)).toFixed(2)} MB · ready to configure`
            : 'Upload the sonar images in respected formats · upto 60 MB'}
        </span>
        <div className={styles.formats}>
          <span className={styles.chip}>TIFF</span>
          <span className={styles.chip}>GEOTIFF</span>
          <span className={styles.chip}>PNG</span>
          <span className={styles.chip}>JPG</span>
        </div>
        <div className={styles.fileActions}>
          <button
            className={styles.btnBrowse}
            type="button"
            onClick={(e) => {
              e.preventDefault()
              inputRef.current?.click()
            }}
          >
            Browse files
          </button>
          {file ? (
            <button
              className={styles.btnRemove}
              type="button"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                onFile(null)
                if (inputRef.current) inputRef.current.value = ''
              }}
            >
              Remove file
            </button>
          ) : null}
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          hidden
          onChange={(e) => takeFile(e.target.files?.[0])}
        />
      </label>
    </section>
  )
}
