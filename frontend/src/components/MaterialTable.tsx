import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import { ITEM_NUMBERS, groupByCategory } from '@/lib/items'

interface MaterialTableProps {
  items: Record<string, number>
  grouped?: boolean
  formulas?: Record<string, string>
}

export function MaterialTable({ items, grouped = false, formulas }: MaterialTableProps) {
  const rows = Object.entries(items)
    .filter(([, qty]) => qty > 0)
    .sort(([a], [b]) => a.localeCompare(b))

  if (rows.length === 0) {
    return <p className="text-muted-foreground text-center py-8">No items in this category.</p>
  }

  if (!grouped) {
    return <FlatTable rows={rows} formulas={formulas} />
  }

  const groups = groupByCategory(items)

  return (
    <div className="flex flex-col gap-1">
      <Table>
        <TableHeader>
          <TableRow className="bg-gray-50">
            <TableHead className="w-20 text-xs">Item #</TableHead>
            <TableHead className="text-xs">Description</TableHead>
            <TableHead className="text-right w-24 text-xs">Qty</TableHead>
            <TableHead className="text-right w-28 text-xs text-gray-400">Unit Price</TableHead>
            <TableHead className="text-right w-28 text-xs text-gray-400">Extended</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {groups.map(({ category, items: catItems }) => (
            <CategoryGroup key={category} category={category} items={catItems} formulas={formulas} />
          ))}
        </TableBody>
      </Table>
      <div className="text-right pr-4 pt-2 border-t-2 border-gray-200">
        <span className="text-sm text-muted-foreground mr-6">Total Line Items:</span>
        <span className="font-mono font-bold text-lg tabular-nums">{rows.length}</span>
      </div>
    </div>
  )
}

function CategoryGroup({ category, items, formulas: _formulas }: {
  category: string
  items: [string, number][]
  formulas?: Record<string, string>
}) {
  const subtotal = items.reduce((sum, [, qty]) => sum + qty, 0)

  return (
    <>
      {/* Category header */}
      <TableRow className="bg-[#1e3a5f]/5 hover:bg-[#1e3a5f]/5">
        <TableCell colSpan={5} className="py-2">
          <span className="text-xs font-bold uppercase tracking-wider text-[#1e3a5f]">
            {category}
          </span>
          <span className="text-xs text-muted-foreground ml-2">
            ({items.length} {items.length === 1 ? 'item' : 'items'})
          </span>
        </TableCell>
      </TableRow>
      {/* Items */}
      {items.map(([name, qty], i) => (
        <TableRow key={name} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}>
          <TableCell className="font-mono tabular-nums text-xs text-muted-foreground py-2">
            {ITEM_NUMBERS[name] ?? '----'}
          </TableCell>
          <TableCell className="py-2 text-sm">{name}</TableCell>
          <TableCell className="text-right font-mono tabular-nums font-medium py-2">
            {qty.toLocaleString()}
          </TableCell>
          <TableCell className="text-right py-2">
            <span className="text-xs text-gray-300">--</span>
          </TableCell>
          <TableCell className="text-right py-2">
            <span className="text-xs text-gray-300">--</span>
          </TableCell>
        </TableRow>
      ))}
      {/* Subtotal */}
      <TableRow className="border-b-2 border-gray-200 hover:bg-transparent">
        <TableCell />
        <TableCell className="text-right text-xs text-muted-foreground py-1.5 italic">
          {category} subtotal
        </TableCell>
        <TableCell className="text-right font-mono tabular-nums text-sm font-semibold py-1.5">
          {subtotal.toLocaleString()}
        </TableCell>
        <TableCell />
        <TableCell />
      </TableRow>
    </>
  )
}

function FlatTable({ rows, formulas }: {
  rows: [string, number][]
  formulas?: Record<string, string>
}) {
  const hasFormulas = formulas && Object.keys(formulas).length > 0

  return (
    <Table>
      <TableHeader>
        <TableRow className="bg-gray-50">
          <TableHead className="w-20 text-xs">Item #</TableHead>
          <TableHead className="text-xs">Description</TableHead>
          <TableHead className="text-right w-24 text-xs">Qty</TableHead>
          {hasFormulas && (
            <TableHead className="text-xs pl-6">Derivation</TableHead>
          )}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map(([name, qty], i) => (
          <TableRow key={name} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'}>
            <TableCell className="font-mono tabular-nums text-xs text-muted-foreground py-2">
              {ITEM_NUMBERS[name] ?? '----'}
            </TableCell>
            <TableCell className="py-2 text-sm">{name}</TableCell>
            <TableCell className="text-right font-mono tabular-nums font-medium py-2">
              {qty.toLocaleString()}
            </TableCell>
            {hasFormulas && (
              <TableCell className="pl-6 py-2">
                {formulas[name] ? (
                  <span className="text-xs text-muted-foreground font-mono">
                    {formulas[name]}
                  </span>
                ) : (
                  <span className="text-xs text-gray-300 italic">reference value</span>
                )}
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
