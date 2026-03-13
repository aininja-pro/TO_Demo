/** Item number mapping — mirrors takeoff_system/output_generator.py ITEM_NUMBERS */
export const ITEM_NUMBERS: Record<string, string | number> = {
  // Conduit
  '3/4" EMT': 1001,
  '1" EMT': 1002,
  '1-1/4" EMT': 1003,
  '1-1/2" EMT': 1004,
  // Fittings - 3/4"
  '3/4" Connector': 1101,
  '3/4" Coupling': 1102,
  '3/4" Bushing': 1103,
  '3/4" 1-Hole Strap': 1104,
  '3/4" Unistrut Strap': 1105,
  // Fittings - 1"
  '1" Connector': 1111,
  '1" Coupling': 1112,
  '1" Bushing': 1113,
  '1" 1-Hole Strap': 1114,
  '1" Unistrut Strap': 1115,
  // Fittings - 1-1/4"
  '1-1/4" Connector': 1121,
  '1-1/4" Coupling': 1122,
  '1-1/4" Bushing': 1123,
  '1-1/4" 1-Hole Strap': 1124,
  '1-1/4" Unistrut Strap': 1125,
  // Fittings - 1/2"
  '1/2" Connector': 1091,
  '1/2" Coupling': 1092,
  '1/2" Bushing': 1093,
  '1/2" 1-Hole Strap': 1094,
  // Wire
  '#12 THHN': 2001,
  '#10 THHN': 2011,
  '#8 THHN': 2021,
  '#3 THHN': 2031,
  // Boxes
  '4" Square Box w/bracket': 3001,
  '4" Square Box': 3002,
  '4-11/16" Square Box w/bracket': 3011,
  '4-11/16" Square Box': 3012,
  '4" Square Box 2-1/8" deep': 3021,
  // Rings
  '4" Square-1G Plaster Ring': 3101,
  '4" Square-2G Plaster Ring': 3102,
  '4" Square-3/0 Plaster Ring': 3103,
  '4-11/16"-1G Plaster Ring': 3111,
  // Plates
  'Duplex Plate': 3201,
  'Decora Plate': 3202,
  'Switch Plate': 3203,
  'Blank Cover': 3204,
  'Blank Cover w/KO': 3205,
  // Consumables
  'Red Wirenut': 4001,
  'Yellow Wirenut': 4002,
  'Ground Screw': 4003,
  'Pan Head Tapping Screw #8': 4004,
  'Poly Pull Line (ft)': 4005,
  'Black Tape': 4006,
  'Red Phase Tape': 4007,
  'Blue Phase Tape': 4008,
  // Technology
  'Cat 6 Jack': 5001,
  'Cat 6 Cable (ft)': 5002,
  'J-Hook': 5003,
  'Floor Box': 5004,
  // Panel equipment
  '20A 1P Breaker': 6001,
  '30A 2P Breaker': 6002,
  '30A/2P Safety Switch 240V': 6011,
  '30A/3P Safety Switch 600V': 6012,
  '100A/3P Safety Switch 600V': 6013,
  // Controls
  'Ceiling Occupancy Sensor': 7001,
  'Wall Occupancy Sensor': 7002,
  'Daylight Sensor': 7003,
  'Wireless Dimmer': 7004,
  'Power Pack': 7005,
  // Power devices
  'Duplex Receptacle': 7101,
  'GFI Receptacle': 7102,
  'SP Switch': 7103,
  '3-Way Switch': 7104,
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
  "4' Linear LED": 'L4',
  "6' Linear LED": 'L6',
  "8' Linear LED": 'L8',
  "10' Linear LED": 'L10',
  "16' Linear LED": 'L16',
  // Pendants
  'F10-22': 'F10-22',
  'F10-30': 'F10-30',
  'F11-4X4': 'F11-4X4',
  'F11-6X6': 'F11-6X6',
  'F11-8X8': 'F11-8X8',
  'F11-10X10': 'F11-10X10',
  'F11-16X10': 'F11-16X10',
  // Accessories
  'Fixture Whip': 8001,
  'Pendant/Cable': 8002,
  'Aircraft Cable Kit': 8003,
  'Canopy Kit': 8004,
  // Demo items
  "Demo 2'x4' Recessed": 'D01',
  "Demo 2'x2' Recessed": 'D02',
  'Demo Downlight': 'D03',
  "Demo 4' Strip": 'D04',
  "Demo 8' Strip": 'D05',
  'Demo Exit': 'D06',
  'Demo Receptacle': 'D07',
  'Demo Floor Box': 'D08',
  'Demo Switch': 'D09',
}

/** Category filter patterns for the materials tab */
const FIXTURE_KEYS = [
  'F2', 'F3', 'F4', 'F4E', 'F5', 'F7', 'F7E', 'F8', 'F9', 'X1', 'X2',
]
const LINEAR_PATTERN = /Linear LED/
const PENDANT_PATTERN = /^F1[01]-/

const CONTROL_KEYS = [
  'Ceiling Occupancy Sensor', 'Wall Occupancy Sensor',
  'Daylight Sensor', 'Wireless Dimmer', 'Power Pack',
]

const POWER_KEYS = [
  'Duplex Receptacle', 'GFI Receptacle', 'SP Switch', '3-Way Switch',
]

const TECH_KEYS = ['Cat 6 Jack', 'Cat 6 Cable (ft)', 'J-Hook', 'Floor Box']

export function filterByCategory(
  materials: Record<string, number>,
  category: string,
): Record<string, number> {
  const result: Record<string, number> = {}
  for (const [key, val] of Object.entries(materials)) {
    if (matchesCategory(key, category)) {
      result[key] = val
    }
  }
  return result
}

function matchesCategory(key: string, category: string): boolean {
  switch (category) {
    case 'fixtures':
      return FIXTURE_KEYS.includes(key) || LINEAR_PATTERN.test(key) || PENDANT_PATTERN.test(key)
    case 'controls':
      return CONTROL_KEYS.includes(key)
    case 'power':
      return POWER_KEYS.includes(key)
    case 'technology':
      return TECH_KEYS.includes(key)
    default:
      return true
  }
}
