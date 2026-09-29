import './Backdrop.css'

export default function Backdrop() {
  return (
    <div className="backdrop" aria-hidden="true">
      <span className="backdrop-orb backdrop-orb-1" />
      <span className="backdrop-orb backdrop-orb-2" />
      <span className="backdrop-orb backdrop-orb-3" />
    </div>
  )
}
