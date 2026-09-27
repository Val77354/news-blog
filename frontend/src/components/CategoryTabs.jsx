import { useEffect, useRef, useState } from 'react'
import { CATEGORIES } from '../constants'
import './CategoryTabs.css'

export default function CategoryTabs({ active, onChange }) {
  const tabs = ['All', ...CATEGORIES]
  const containerRef = useRef(null)
  const tabRefs = useRef({})
  const [indicatorStyle, setIndicatorStyle] = useState({ width: 0, left: 0 })

  useEffect(() => {
    const activeKey = active === null ? 'All' : active
    const node = tabRefs.current[activeKey]
    const container = containerRef.current
    if (node && container) {
      const nodeRect = node.getBoundingClientRect()
      const containerRect = container.getBoundingClientRect()
      setIndicatorStyle({
        width: nodeRect.width,
        left: nodeRect.left - containerRect.left,
      })
    }
  }, [active])

  return (
    <div className="category-tabs" ref={containerRef}>
      <span className="category-tab-indicator" style={indicatorStyle} />
      {tabs.map((tab) => {
        const isActive = tab === 'All' ? active === null : active === tab
        return (
          <button
            key={tab}
            type="button"
            ref={(el) => {
              tabRefs.current[tab] = el
            }}
            className={`category-tab${isActive ? ' active' : ''}`}
            onClick={() => onChange(tab === 'All' ? null : tab)}
          >
            {tab}
          </button>
        )
      })}
    </div>
  )
}
