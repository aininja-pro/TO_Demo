interface HeaderProps {
  children?: React.ReactNode
}

export function Header({ children }: HeaderProps) {
  return (
    <header className="bg-[#1e3a5f] text-white px-6 py-4 flex items-center justify-between">
      <h1 className="text-xl font-semibold tracking-tight">MEP Takeoff Pro</h1>
      {children && <div className="flex items-center gap-3">{children}</div>}
    </header>
  )
}
