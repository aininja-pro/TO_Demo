import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { TakeoffResults, MaterialCategory } from '@/lib/types'
import { filterByCategory } from '@/lib/items'
import { StatsBar } from './StatsBar'
import { MaterialTable } from './MaterialTable'

interface ResultsDashboardProps {
  results: TakeoffResults
}

export function ResultsDashboard({ results }: ResultsDashboardProps) {
  const [tab, setTab] = useState<MaterialCategory>('all')

  const allMaterials = { ...results.materials, ...results.derived_materials, ...results.demo_items }

  function getItemsForTab(category: MaterialCategory): Record<string, number> {
    switch (category) {
      case 'all':
        return allMaterials
      case 'demo':
        return results.demo_items
      case 'derived':
        return results.derived_materials
      default:
        return filterByCategory(results.materials, category)
    }
  }

  function exportCsv() {
    const rows = Object.entries(allMaterials)
      .filter(([, qty]) => qty > 0)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([name, qty]) => `"${name}",${qty}`)
    const csv = `"Description","Qty"\n${rows.join('\n')}`
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'takeoff_materials.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  const tabs: { value: MaterialCategory; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'fixtures', label: 'Fixtures' },
    { value: 'controls', label: 'Controls' },
    { value: 'power', label: 'Power' },
    { value: 'technology', label: 'Tech' },
    { value: 'demo', label: 'Demo' },
    { value: 'derived', label: 'Derived' },
  ]

  return (
    <div className="flex flex-col gap-6">
      <StatsBar results={results} />

      <Tabs value={tab} onValueChange={(v) => setTab(v as MaterialCategory)}>
        <div className="flex items-center justify-between">
          <TabsList>
            {tabs.map(t => (
              <TabsTrigger key={t.value} value={t.value}>{t.label}</TabsTrigger>
            ))}
          </TabsList>
          <button
            onClick={exportCsv}
            className="text-sm text-[#2563eb] hover:underline"
          >
            Export CSV
          </button>
        </div>

        {tabs.map(t => (
          <TabsContent key={t.value} value={t.value}>
            <MaterialTable items={getItemsForTab(t.value)} />
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}
