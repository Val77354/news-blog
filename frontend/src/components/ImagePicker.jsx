import { useEffect, useState } from 'react'
import { resolveImageUrl } from '../api/posts'
import './PostForm.css'

// "Choose image" button with a preview. The parent uploads the chosen file on save.
export default function ImagePicker({ initialUrl, onFileSelected, caption = 'Image (optional)' }) {
  const [previewUrl, setPreviewUrl] = useState(resolveImageUrl(initialUrl))

  useEffect(() => {
    return () => {
      if (previewUrl && previewUrl.startsWith('blob:')) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  function handleChange(e) {
    const file = e.target.files[0]
    if (!file) return
    onFileSelected(file)
    setPreviewUrl(URL.createObjectURL(file))
  }

  return (
    <div className="post-form-image-field">
      <span className="post-form-image-caption">{caption}</span>
      <div className="post-form-image-picker">
        {previewUrl && <img src={previewUrl} alt="" className="post-form-image-preview" />}
        <label className="post-form-file-button">
          {previewUrl ? 'Change image' : 'Choose image'}
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            className="post-form-file-input"
            onChange={handleChange}
          />
        </label>
      </div>
    </div>
  )
}
