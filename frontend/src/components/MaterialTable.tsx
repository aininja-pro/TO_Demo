import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import { ITEM_NUMBERS } from '@/lib/items'

interface MaterialTableProps {
  items: Record<string, number>
}

export function MaterialTable({ items }: MaterialTableProps) {
  const rows = Object.entries(items)
    .filter(([, qty]) => qty > 0)
    .sort(([a], [b]) => a.localeCompare(b))

  if (rows.length === 0) {
    return <p className="text-muted-foreground text-center py-8">No items in this category.</p>
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-24">Item #</TableHead>
          <TableHead>Description</TableHead>
          <TableHead className="text-right w-28">Qty</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map(([name, qty]) => (
          <TableRow key={name}>
            <TableCell className="font-mono tabular-nums text-muted-foreground">
              {ITEM_NUMBERS[name] ?? '----'}
            </TableCell>
            <TableCell>{name}</TableCell>
            <TableCell className="text-right font-mono tabular-nums">{qty.toLocaleString()}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
