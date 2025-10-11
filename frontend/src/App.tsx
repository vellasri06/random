import { useMemo, useRef, useState } from 'react'
import './App.css'
import { generateMom } from './api'
import type { ActionItem, MomResponse } from './types'
import { Collapsible } from './components/Collapsible'

function App() {
  const [transcript, setTranscript] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mom, setMom] = useState<MomResponse['mom'] | null>(null)
  const [pdfId, setPdfId] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const canSubmit = useMemo(() => {
    return (transcript && transcript.trim().length > 0) || file !== null
  }, [transcript, file])

  async function onSubmit() {
    setError(null)
    setLoading(true)
    try {
      const result = await generateMom({ transcript, file })
      setMom(result.mom)
      setPdfId(result.pdf_id)
    } catch (e: any) {
      setError(e?.message || 'Failed to generate MoM')
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setTranscript('')
    setFile(null)
    setMom(null)
    setPdfId(null)
    setError(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const pdfUrl = pdfId ? `${apiBase}/download/${pdfId}` : null

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-5xl px-4 py-4">
          <h1 className="text-2xl font-semibold text-gray-900">Automated MoM Generator</h1>
          <p className="text-sm text-gray-500">Paste a transcript or upload a .txt/.vtt file</p>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-6">
        <div className="grid gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Meeting Transcript</label>
            <textarea
              className="w-full min-h-48 rounded-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Paste raw meeting notes or transcript here..."
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
            />

            <div className="mt-3 flex items-center gap-3">
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.vtt"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-500 file:mr-4 file:rounded file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-blue-700 hover:file:bg-blue-100"
              />
              {file && (
                <span className="text-xs text-gray-600">Selected: {file.name}</span>
              )}
            </div>

            <div className="mt-4 flex gap-2">
              <button
                onClick={onSubmit}
                disabled={!canSubmit || loading}
                className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
              >
                {loading && (
                  <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                )}
                Generate MoM
              </button>
              <button
                onClick={reset}
                disabled={loading}
                className="rounded-md border px-4 py-2 text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Reset
              </button>
              {pdfUrl && (
                <a
                  href={pdfUrl}
                  target="_blank"
                  className="ml-auto rounded-md border px-4 py-2 text-gray-700 hover:bg-gray-50"
                >
                  Download as PDF
                </a>
              )}
            </div>

            {error && (
              <div className="mt-3 rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">{error}</div>
            )}
          </div>

          {mom && (
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-semibold">Minutes of Meeting</h2>
              <div className="mt-2 grid gap-2">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <div>
                    <div className="text-sm text-gray-500">Meeting Title</div>
                    <div className="font-medium">{mom.meeting_title || 'Meeting'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Date</div>
                    <div className="font-medium">{mom.date || '-'}</div>
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Attendees</div>
                  <div className="font-medium">{(mom.attendees || []).join(', ') || '-'}</div>
                </div>
              </div>

              <div className="mt-4">
                <Collapsible title="Executive Summary" defaultOpen>
                  <p className="text-gray-800 leading-7 whitespace-pre-wrap">{mom.executive_summary || '-'}</p>
                </Collapsible>
              </div>

              <div className="mt-2">
                <Collapsible title="Key Decisions Made">
                  {(mom.key_decisions || []).length === 0 ? (
                    <div className="text-gray-600">-</div>
                  ) : (
                    <ul className="list-disc pl-6 space-y-1">
                      {mom.key_decisions.map((d, i) => (
                        <li key={i}>{d}</li>
                      ))}
                    </ul>
                  )}
                </Collapsible>
              </div>

              <div className="mt-2">
                <Collapsible title="Action Items">
                  {(mom.action_items || []).length === 0 ? (
                    <div className="text-gray-600">-</div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="min-w-full border border-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-2 text-left text-sm font-semibold text-gray-700 border-b">Task</th>
                            <th className="px-3 py-2 text-left text-sm font-semibold text-gray-700 border-b">Assigned To</th>
                            <th className="px-3 py-2 text-left text-sm font-semibold text-gray-700 border-b">Deadline</th>
                          </tr>
                        </thead>
                        <tbody>
                          {mom.action_items.map((it: ActionItem, i: number) => (
                            <tr key={i} className="odd:bg-white even:bg-gray-50">
                              <td className="px-3 py-2 border-b align-top">{it.task || '-'}</td>
                              <td className="px-3 py-2 border-b align-top">{it.assigned_to || '-'}</td>
                              <td className="px-3 py-2 border-b align-top">{it.deadline || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </Collapsible>
              </div>

              {mom.formatted_markdown && (
                <div className="mt-2">
                  <Collapsible title="Formatted Markdown (LLM)">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800">{mom.formatted_markdown}</pre>
                  </Collapsible>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
