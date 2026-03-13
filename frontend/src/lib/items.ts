/** Item number mapping — uses client's actual item numbers from IVCC CETLA Material List PDF */
export const ITEM_NUMBERS: Record<string, string | number> = {
  // Conduit
  '1/2" EMT': 1000,
  '3/4" EMT': 1001,
  '1" EMT': 1002,
  '1-1/4" EMT': 1003,
  '3/4" Steel Flex': 1122,
  '3/4" Liquidtight': 1144,
  // Fittings - 1/2"
  '1/2" Connector': 1484,
  '1/2" Coupling': 1564,
  '1/2" Bushing': 1606,
  '1/2" 1-Hole Strap': 2338,
  // Fittings - 3/4"
  '3/4" Connector': 1485,
  '3/4" Coupling': 1565,
  '3/4" Bushing': 1607,
  '3/4" 1-Hole Strap': 2339,
  '3/4" Unistrut Strap': 2371,
  '3/4" LT Flex Connector': 1924,
  // Fittings - 1"
  '1" Connector': 1486,
  '1" Coupling': 1566,
  '1" Bushing': 1608,
  '1" 1-Hole Strap': 2340,
  '1" Unistrut Strap': 2372,
  // Fittings - 1-1/4"
  '1-1/4" Connector': 1487,
  '1-1/4" Coupling': 1567,
  '1-1/4" Bushing': 1609,
  '1-1/4" 1-Hole Strap': 2341,
  '1-1/4" Unistrut Strap': 2373,
  // Wire
  '#12 THHN': 2660,
  '#10 THHN': 2661,
  '#8 THHN': 2662,
  '#3 THHN': 2665,
  // Boxes
  '4" Square Box': 2469,
  '4" Square Box w/bracket': 2470,
  '4" Square Box 2-1/8" deep': 2472,
  '4-11/16" Square Box': 2476,
  '4-11/16" Square Box w/bracket': 2477,
  // Rings
  '4" Square-1G Plaster Ring': 4897,
  '4" Square-2G Plaster Ring': 4902,
  '4" Square-3/0 Plaster Ring': '4891/92',
  '4-11/16"-1G Plaster Ring': 4925,
  // Plates
  'Decora Plate': 4949,
  'Duplex Plate': 4950,
  'Switch Plate': 4953,
  'Duplex Plate 2G': 4959,
  'Blank Cover': 5079,
  'Blank Cover w/KO': '5080/82',
  // Consumables
  'Red Wirenut': 6133,
  'Red Scotchlok': 5297,
  'Ground Screw w/Pigtail': 7114,
  'Pan Head Screw': 7123,
  'Ground Screw': 7124,
  'Poly Pull Line (ft)': 3078,
  // Technology
  'Cat 6 Jack': 28661,
  'Cat 6 Cable (ft)': 2935,
  'J-Hook': 62844,
  // Panel equipment
  '20A 1P Breaker': 3934,
  '30A 2P Breaker': 3945,
  '30A/2P Safety Switch 240V': 3191,
  '30A/3P Safety Switch 600V': 3255,
  '100A/3P Safety Switch 600V': 'FDS-ELEV',
  // Controls
  'Ceiling Occupancy Sensor': 62693,
  'Wall Occupancy Sensor': 62701,
  'Daylight Sensor': 62687,
  'Wireless Dimmer': 48615,
  'Power Pack': 4887,
  // Power devices
  'Duplex Receptacle': 4703,
  'GFI Receptacle': 4712,
  'SP Switch': 4648,
  '3-Way Switch': 4673,
  // Fixtures
  'F2': 'F2',
  'F3': 'F3',
  'F4': 'F4',
  'F4E': 'F4E',
  'F5': 'F5',
  'F7': 'F7',
  'F7E': 'F7E',
  'F8': 'F8',
  'F9': 'F9',
  'X1': 'X1',
  'X2': 'X2',
  // Linear LEDs
  "4' Linear LED": 62880,
  "6' Linear LED": 63014,
  "8' Linear LED": 62881,
  "10' Linear LED": 63012,
  "16' Linear LED": 62882,
  "4' L.E.D. Strip": '4 STRIP',
  // Pendants
  'F10-22': 'F10-22',
  'F10-30': 'F10-30',
  'F11-4X4': 'F11-4X4',
  'F11-6X6': 'F11-6X6',
  'F11-8X8': 'F11-8X8',
  'F11-10X10': 'F1110X10',
  'F11-16X10': 'F1116X10',
  // Accessories
  'Fixture Whip': 5294,
  'Pendant/Cable': 5261,
  'Seismic Wire': 5257,
  // Demo items
  "Demo 2'x4' Recessed": 10125,
  "Demo 2'x2' Recessed": 10127,
  'Demo Downlight': 10128,
  "Demo 4' Strip": 10132,
  "Demo 8' Strip": 10133,
  'Demo Exit': 10136,
  'Demo Receptacle': 10173,
  'Demo Floor Box': 10178,
  'Demo Switch': 10218,
  // Hardware & Support
  'T-Bar Conduit Clip': 2425,
  '3/8" All Thread': 2445,
  '3/8" Hex Nut': 2447,
  '3/8" Beam Clamp': 2451,
  'Core Floor Penetration': 2064,
  '12x12x6" Pull Box': 5763,
  'Unistrut (Deep)': 5932,
  // Labor & Project Tasks
  'Wire Termination Labor': 4409,
  'Channel Cut (labor)': 5935,
  'Disconnect Elevator Power': 'T0001',
  'Relocate Junction Boxes': 'T0002',
  'Demo "Make Safe"': 'T0003',
  'Temporary Power & Light': 'T0004',
}

/** Category definitions for grouping materials */
export type ItemCategory =
  | 'Fixtures' | 'Linear LEDs' | 'Pendants' | 'Controls' | 'Power'
  | 'Panel' | 'Demo' | 'Technology' | 'Conduit' | 'Fittings'
  | 'Wire' | 'Boxes' | 'Rings' | 'Plates' | 'Consumables' | 'Accessories'
  | 'Hardware' | 'Labor & Tasks'

export const CATEGORY_ORDER: ItemCategory[] = [
  'Fixtures', 'Linear LEDs', 'Pendants', 'Controls', 'Power',
  'Panel', 'Demo', 'Technology', 'Conduit', 'Fittings',
  'Wire', 'Boxes', 'Rings', 'Plates', 'Consumables', 'Accessories',
  'Hardware', 'Labor & Tasks',
]

const FIXTURE_KEYS = ['F2', 'F3', 'F4', 'F4E', 'F5', 'F7', 'F7E', 'F8', 'F9', 'X1', 'X2']
const PENDANT_PATTERN = /^F1[01]-/
const LINEAR_PATTERN = /Linear LED/
const CONTROL_KEYS = ['Ceiling Occupancy Sensor', 'Wall Occupancy Sensor', 'Daylight Sensor', 'Wireless Dimmer', 'Power Pack']
const POWER_KEYS = ['Duplex Receptacle', 'GFI Receptacle', 'SP Switch', '3-Way Switch']
const TECH_KEYS = ['Cat 6 Jack', 'Cat 6 Cable (ft)', 'J-Hook', 'Floor Box']
const PANEL_KEYS = ['20A 1P Breaker', '30A 2P Breaker', '30A/2P Safety Switch 240V', '30A/3P Safety Switch 600V', '100A/3P Safety Switch 600V']
const CONDUIT_PATTERN = /EMT$/
const CONDUIT_KEYS = ['3/4" Steel Flex', '3/4" Liquidtight']
const FITTING_PATTERN = /Connector$|Coupling$|Bushing$|1-Hole Strap$|Unistrut Strap$/
const FITTING_KEYS = ['3/4" LT Flex Connector']
const WIRE_PATTERN = /THHN$/
const BOX_PATTERN = /Square Box/
const BOX_KEYS = ['12x12x6" Pull Box']
const RING_PATTERN = /Plaster Ring/
const PLATE_KEYS = ['Duplex Plate', 'Decora Plate', 'Switch Plate', 'Blank Cover', 'Blank Cover w/KO', 'Duplex Plate 2G']
const CONSUMABLE_KEYS = ['Red Wirenut', 'Red Scotchlok', 'Ground Screw w/Pigtail', 'Ground Screw', 'Pan Head Screw', 'Poly Pull Line (ft)']
const ACCESSORY_KEYS = ['Fixture Whip', 'Pendant/Cable', 'Seismic Wire']
const HARDWARE_KEYS = ['T-Bar Conduit Clip', '3/8" All Thread', '3/8" Hex Nut', '3/8" Beam Clamp', 'Core Floor Penetration', 'Unistrut (Deep)']
const LABOR_KEYS = ['Wire Termination Labor', 'Channel Cut (labor)', 'Disconnect Elevator Power', 'Relocate Junction Boxes', 'Demo "Make Safe"', 'Temporary Power & Light']

export function getItemCategory(key: string): ItemCategory | null {
  if (FIXTURE_KEYS.includes(key)) return 'Fixtures'
  if (LINEAR_PATTERN.test(key)) return 'Linear LEDs'
  if (key.startsWith("4' L.E.D.")) return 'Linear LEDs'
  if (PENDANT_PATTERN.test(key)) return 'Pendants'
  if (CONTROL_KEYS.includes(key)) return 'Controls'
  if (POWER_KEYS.includes(key)) return 'Power'
  if (PANEL_KEYS.includes(key)) return 'Panel'
  if (key.startsWith('Demo')) return 'Demo'
  if (TECH_KEYS.includes(key)) return 'Technology'
  if (CONDUIT_PATTERN.test(key) || CONDUIT_KEYS.includes(key)) return 'Conduit'
  if (FITTING_PATTERN.test(key) || FITTING_KEYS.includes(key)) return 'Fittings'
  if (WIRE_PATTERN.test(key)) return 'Wire'
  if (BOX_PATTERN.test(key) || BOX_KEYS.includes(key)) return 'Boxes'
  if (RING_PATTERN.test(key)) return 'Rings'
  if (PLATE_KEYS.includes(key)) return 'Plates'
  if (CONSUMABLE_KEYS.includes(key)) return 'Consumables'
  if (ACCESSORY_KEYS.includes(key)) return 'Accessories'
  if (HARDWARE_KEYS.includes(key)) return 'Hardware'
  if (LABOR_KEYS.includes(key)) return 'Labor & Tasks'
  return null
}

/** Group items by category, ordered by CATEGORY_ORDER */
export function groupByCategory(items: Record<string, number>): { category: ItemCategory; items: [string, number][] }[] {
  const groups = new Map<ItemCategory, [string, number][]>()

  for (const [key, val] of Object.entries(items)) {
    if (val <= 0) continue
    const cat = getItemCategory(key)
    if (!cat) continue
    if (!groups.has(cat)) groups.set(cat, [])
    groups.get(cat)!.push([key, val])
  }

  // Sort items within each group by item number
  for (const items of groups.values()) {
    items.sort(([a], [b]) => a.localeCompare(b))
  }

  return CATEGORY_ORDER
    .filter(cat => groups.has(cat))
    .map(cat => ({ category: cat, items: groups.get(cat)! }))
}

/** Legacy filter (kept for backward compat with tabs) */
export function filterByCategory(
  materials: Record<string, number>,
  category: string,
): Record<string, number> {
  const result: Record<string, number> = {}
  for (const [key, val] of Object.entries(materials)) {
    const itemCat = getItemCategory(key)
    if (itemCat && itemCat.toLowerCase().replace(/\s+/g, '') === category.replace(/\s+/g, '')) {
      result[key] = val
    }
  }
  return result
}
