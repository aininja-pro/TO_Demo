import { Zap } from 'lucide-react'

interface HeaderProps {
  children?: React.ReactNode
}

export function Header({ children }: HeaderProps) {
  return (
    <header className="bg-card border-b border-border px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2.5">
        <div className="text-primary">
          <Zap className="h-4.5 w-4.5" />
        </div>
        <div className="flex items-baseline gap-2">
          <h1 className="text-sm font-semibold tracking-tight text-foreground">MEP Takeoff Pro</h1>
          <span className="text-[10px] text-muted-foreground font-medium tracking-widest uppercase">Electrical Estimating</span>
        </div>
      </div>
      {children && <div className="flex items-center gap-2">{children}</div>}
    </header>
  )
}
