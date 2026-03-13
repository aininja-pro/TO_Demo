import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Download, Printer } from 'lucide-react'
import type { TakeoffResults, MaterialCategory } from '@/lib/types'
import { StatsBar } from './StatsBar'
import { MaterialTable } from './MaterialTable'
import { AccuracyComparison } from './AccuracyComparison'

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
        // For 'fixtures', 'controls', 'power', 'technology' — filter from counted materials
        return filterBySimpleCategory(results.materials, category)
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

  function printReport() {
    window.print()
  }

  const tabs: { value: MaterialCategory; label: string }[] = [
    { value: 'all', label: 'All Items' },
    { value: 'fixtures', label: 'Fixtures' },
    { value: 'controls', label: 'Controls' },
    { value: 'power', label: 'Power' },
    { value: 'technology', label: 'Tech' },
    { value: 'demo', label: 'Demo' },
    { value: 'derived', label: 'Derived' },
  ]

  const hasValidation = results.validation && results.validation.length > 0

  return (
    <div className="flex flex-col gap-6">
      <StatsBar results={results} />

      <Tabs value={tab} onValueChange={(v) => setTab(v as MaterialCategory)}>
        <div className="flex items-center justify-between flex-wrap gap-2">
          <TabsList>
            {tabs.map(t => (
              <TabsTrigger key={t.value} value={t.value}>{t.label}</TabsTrigger>
            ))}
            {hasValidation && (
              <TabsTrigger value="accuracy" className="text-green-700 data-[state=active]:text-green-800">
                Accuracy
              </TabsTrigger>
            )}
          </TabsList>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={exportCsv} className="gap-1.5 text-xs">
              <Download className="h-3.5 w-3.5" />
              CSV
            </Button>
            <Button variant="outline" size="sm" onClick={printReport} className="gap-1.5 text-xs">
              <Printer className="h-3.5 w-3.5" />
              Print
            </Button>
          </div>
        </div>

        {/* All Items — grouped view */}
        <TabsContent value="all">
          <MaterialTable items={allMaterials} grouped />
        </TabsContent>

        {/* Category-filtered views */}
        {tabs.filter(t => t.value !== 'all').map(t => (
          <TabsContent key={t.value} value={t.value}>
            <MaterialTable
              items={getItemsForTab(t.value)}
              formulas={t.value === 'derived' ? results.formulas : undefined}
            />
          </TabsContent>
        ))}

        {/* Accuracy tab */}
        {hasValidation && (
          <TabsContent value="accuracy">
            <AccuracyComparison validation={results.validation} />
          </TabsContent>
        )}
      </Tabs>

      {/* Pricing CTA */}
      <div className="text-center py-4 border border-dashed border-gray-300 rounded-lg bg-gray-50/50">
        <p className="text-sm text-gray-500">
          Unit pricing columns available when connected to your pricing database
        </p>
      </div>
    </div>
  )
}

/** Simple category filter for the tab views */
function filterBySimpleCategory(materials: Record<string, number>, category: string): Record<string, number> {
  const CATEGORY_KEYS: Record<string, string[]> = {
    fixtures: ['F2', 'F3', 'F4', 'F4E', 'F5', 'F7', 'F7E', 'F8', 'F9', 'X1', 'X2'],
    controls: ['Ceiling Occupancy Sensor', 'Wall Occupancy Sensor', 'Daylight Sensor', 'Wireless Dimmer', 'Power Pack'],
    power: ['Duplex Receptacle', 'GFI Receptacle', 'SP Switch', '3-Way Switch'],
    technology: ['Cat 6 Jack', 'Cat 6 Cable (ft)', 'J-Hook', 'Floor Box'],
  }
  const CATEGORY_PATTERNS: Record<string, RegExp[]> = {
    fixtures: [/Linear LED/, /^F1[01]-/],
  }

  const keys = CATEGORY_KEYS[category] ?? []
  const patterns = CATEGORY_PATTERNS[category] ?? []
  const result: Record<string, number> = {}

  for (const [key, val] of Object.entries(materials)) {
    if (keys.includes(key) || patterns.some(p => p.test(key))) {
      result[key] = val
    }
  }
  return result
}
