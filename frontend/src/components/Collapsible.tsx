import { useState, type ReactNode } from 'react'

export function Collapsible({ title, defaultOpen = false, children }: { title: string; defaultOpen?: boolean; children: ReactNode }) {
  const [open, setOpen] = useState<boolean>(defaultOpen)
  return (
    <div className="rounded border border-gray-200">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between bg-gray-50 px-3 py-2 hover:bg-gray-100"
      >
        <span className="text-sm font-medium text-gray-800">{title}</span>
        <span className="text-gray-500">{open ? '−' : '+'}</span>
      </button>
      {open && <div className="px-3 py-3">{children}</div>}
    </div>
  )
}
