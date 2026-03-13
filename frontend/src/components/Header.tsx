import { Zap } from 'lucide-react'

interface HeaderProps {
  children?: React.ReactNode
}

export function Header({ children }: HeaderProps) {
  return (
    <header className="bg-gradient-to-r from-[#1e3a5f] to-[#2d5a8e] text-white px-6 py-4 flex items-center justify-between shadow-md">
      <div className="flex items-center gap-2.5">
        <div className="bg-white/15 rounded-lg p-1.5">
          <Zap className="h-5 w-5 text-amber-300" />
        </div>
        <div>
          <h1 className="text-lg font-semibold tracking-tight leading-tight">MEP Takeoff Pro</h1>
          <p className="text-[11px] text-white/60 font-medium tracking-wide uppercase">Automated Electrical Estimating</p>
        </div>
      </div>
      {children && <div className="flex items-center gap-3">{children}</div>}
    </header>
  )
}
