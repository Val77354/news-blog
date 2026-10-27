// A labelled form field that shows its own error message underneath.
export default function FormField({ label, error, hint, children }) {
  return (
    <label className={error ? 'form-field has-error' : 'form-field'}>
      {label}
      {children}
      {error ? <span className="field-error" role="alert">{error}</span> : hint && <span className="field-hint">{hint}</span>}
    </label>
  )
}
