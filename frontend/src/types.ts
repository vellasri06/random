export type ActionItem = {
  task?: string | null
  assigned_to?: string | null
  deadline?: string | null
}

export type Mom = {
  meeting_title: string
  date?: string | null
  attendees: string[]
  executive_summary: string
  key_decisions: string[]
  action_items: ActionItem[]
  formatted_markdown?: string
}

export type MomResponse = {
  mom: Mom
  pdf_id: string
}
