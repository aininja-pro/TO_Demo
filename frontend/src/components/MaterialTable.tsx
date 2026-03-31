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
    return <p className="text-muted-foreground text-center py-8 text-sm">No items in this category.</p>
  }

  if (!grouped) {
    return <FlatTable rows={rows} formulas={formulas} />
  }

  const groups = groupByCategory(items)

  return (
    <div className="flex flex-col gap-1">
      <Table>
        <TableHeader>
          <TableRow className="bg-secondary/50 hover:bg-secondary/50">
            <TableHead className="w-20">Item #</TableHead>
            <TableHead>Description</TableHead>
            <TableHead className="text-right w-24">Qty</TableHead>
            <TableHead className="text-right w-28 text-muted-foreground/50">Unit Price</TableHead>
            <TableHead className="text-right w-28 text-muted-foreground/50">Extended</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {groups.map(({ category, items: catItems }) => (
            <CategoryGroup key={category} category={category} items={catItems} formulas={formulas} />
          ))}
        </TableBody>
      </Table>
      <div className="text-right pr-3 pt-3 border-t border-border">
        <span className="text-xs text-muted-foreground mr-4">Total Line Items</span>
        <span className="font-mono font-semibold text-base tabular-nums text-foreground">{rows.length}</span>
      </div>
    </div>
  )
}

function CategoryGroup({ category, items }: {
  category: string
  items: [string, number][]
}) {
  const subtotal = items.reduce((sum, [, qty]) => sum + qty, 0)

  return (
    <>
      {/* Category header */}
      <TableRow className="bg-accent/50 hover:bg-accent/50 border-b-0">
        <TableCell colSpan={5} className="py-1.5">
          <span className="text-[10px] font-semibold uppercase tracking-widest text-primary">
            {category}
          </span>
          <span className="text-[10px] text-muted-foreground ml-2 font-mono">
            {items.length}
          </span>
        </TableCell>
      </TableRow>
      {/* Items */}
      {items.map(([name, qty]) => (
        <TableRow key={name} className="hover:bg-accent/30">
          <TableCell className="font-mono tabular-nums text-xs text-muted-foreground py-1.5">
            {ITEM_NUMBERS[name] ?? '—'}
          </TableCell>
          <TableCell className="py-1.5 text-sm text-foreground">{name}</TableCell>
          <TableCell className="text-right font-mono tabular-nums font-medium py-1.5 text-foreground">
            {qty.toLocaleString()}
          </TableCell>
          <TableCell className="text-right py-1.5">
            <span className="text-xs text-muted-foreground/30">—</span>
          </TableCell>
          <TableCell className="text-right py-1.5">
            <span className="text-xs text-muted-foreground/30">—</span>
          </TableCell>
        </TableRow>
      ))}
      {/* Subtotal */}
      <TableRow className="border-b border-border hover:bg-transparent">
        <TableCell />
        <TableCell className="text-right text-[10px] text-muted-foreground py-1 uppercase tracking-wider">
          {category} subtotal
        </TableCell>
        <TableCell className="text-right font-mono tabular-nums text-sm font-semibold py-1 text-foreground">
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
        <TableRow className="bg-secondary/50 hover:bg-secondary/50">
          <TableHead className="w-20">Item #</TableHead>
          <TableHead>Description</TableHead>
          <TableHead className="text-right w-24">Qty</TableHead>
          {hasFormulas && (
            <TableHead className="pl-6">Derivation</TableHead>
          )}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map(([name, qty]) => (
          <TableRow key={name} className="hover:bg-accent/30">
            <TableCell className="font-mono tabular-nums text-xs text-muted-foreground py-1.5">
              {ITEM_NUMBERS[name] ?? '—'}
            </TableCell>
            <TableCell className="py-1.5 text-sm text-foreground">{name}</TableCell>
            <TableCell className="text-right font-mono tabular-nums font-medium py-1.5 text-foreground">
              {qty.toLocaleString()}
            </TableCell>
            {hasFormulas && (
              <TableCell className="pl-6 py-1.5">
                {formulas[name] ? (
                  <span className="text-[11px] text-muted-foreground font-mono">
                    {formulas[name]}
                  </span>
                ) : (
                  <span className="text-[11px] text-muted-foreground/40 font-mono">ref</span>
                )}
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
