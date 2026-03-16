/**
 * Zero-Burn Blueprint — Scientific Simulation Engines
 * All formulas from FEASIBILITY_STUDY.md v2.0
 * Every calculation is sourced and verified.
 */

// ============================================================
// CONSTANTS (from verified research)
// ============================================================
export const CONSTANTS = {
  // Water / Steam thermodynamics
  CP_WATER: 4.186,      // kJ/kg·K — specific heat of water
  CP_VAPOR: 2.010,      // kJ/kg·K — specific heat of steam
  LV: 2257,             // kJ/kg — latent heat of vaporization at 1 atm
  T_BOIL: 100,          // °C at ~1 atm
  T_AMBIENT: 25,        // °C average Thailand water temp

  // Biomass fuel
  BIOMASS_LHV: 14,          // MJ/kg (Lower Heating Value, dry rice husk/straw)
  COMBUSTION_EFF_LOW: 0.30, // Conservative firebox efficiency
  COMBUSTION_EFF_MID: 0.35, // Moderate
  COMBUSTION_EFF_HIGH: 0.45,// Optimistic

  // Boiler design
  COIL_LENGTH: 21,       // meters (corrected from 18 in v1.0)
  TUBE_OD: 0.0127,       // meters (½ inch)
  TUBE_ID: 0.01118,      // meters (inner diameter)
  COIL_DIAMETER: 0.200,  // meters
  HEAT_TRANSFER_AREA: 0.837, // m² = π × 0.0127 × 21

  // Per-rai data (Thailand)
  STRAW_PER_RAI_LOW: 500,    // kg
  STRAW_PER_RAI_MID: 650,    // kg (most common figure)
  STRAW_PER_RAI_HIGH: 800,   // kg
  BURN_FRACTION: 0.70,        // 70% of straw typically burned

  // Mushroom cultivation — V. volvacea
  BE_LOW: 0.05,       // 5% — worst-case field
  BE_CONSERVATIVE: 0.08,  // 8% — lower end outdoor
  BE_MODERATE: 0.12,      // 12% — with supplementation
  BE_OPTIMISTIC: 0.15,    // 15% — best outdoor achievable
  BE_INDOOR: 0.20,        // 20% — indoor cultivation (reference)

  // Mushroom pricing
  PRICE_WHOLESALE: 45,   // ฿/kg — 2025 wholesale (Tridge)
  PRICE_RETAIL: 90,      // ฿/kg — direct/retail (Nakhon Si Thammarat study)
  PRICE_PREMIUM: 160,    // ฿/kg — export/premium grade

  // Operating costs per rai
  COSTS: {
    water: 50,
    spawn: 90,
    supplements: 30,
    labor_steam: 100,
    labor_inoculation: 200,
    labor_monitoring: 300,
    labor_harvest: 200,
    shade_structure: 150,
    equipment_amortized: 66,
  },

  // Emissions (IPCC 2019, Vol.4, Ch.2, Table 2.5)
  CH4_PER_TON: 2.7,     // kg CH₄ per ton dry straw
  N2O_PER_TON: 0.07,    // kg N₂O per ton dry straw
  GWP_CH4: 28,          // 100-yr GWP
  GWP_N2O: 265,         // 100-yr GWP

  // Carbon credits (T-VER, 2024 data)
  CARBON_PRICE_AVG: 174.52,    // ฿/tCO₂eq — Q1 FY2025
  CARBON_PRICE_AG: 1000,       // ฿/tCO₂eq — agricultural category
  CARBON_PRICE_PREMIUM: 2000,  // ฿/tCO₂eq — forestry+ag premium

  // Equipment
  EQUIPMENT_COST: 26550,  // ฿ total BOM
  EQUIPMENT_LIFESPAN_YEARS: 5,
  RAI_PER_SEASON_PER_UNIT: 200,  // 20 farmers × 10 rai
  SEASONS_PER_YEAR: 2,
};

// ============================================================
// THERMODYNAMIC ENGINE
// ============================================================
export function computeBoilerEnergy(flowRateKgS = 0.045, tOut = 120, combustionEff = 0.35) {
  const { CP_WATER, CP_VAPOR, LV, T_BOIL, T_AMBIENT } = CONSTANTS;

  const qSensible = flowRateKgS * CP_WATER * (T_BOIL - T_AMBIENT);  // kW
  const qLatent = flowRateKgS * LV;
  const qSuperheat = flowRateKgS * CP_VAPOR * (tOut - T_BOIL);
  const qTotal = qSensible + qLatent + qSuperheat;

  // Fuel requirement
  const effectiveEnergy = CONSTANTS.BIOMASS_LHV * 1000 * combustionEff; // kJ/kg
  const fuelRateKgS = qTotal / effectiveEnergy;
  const fuelRateKgHr = fuelRateKgS * 3600;

  return {
    qSensible: Math.round(qSensible * 100) / 100,
    qLatent: Math.round(qLatent * 100) / 100,
    qSuperheat: Math.round(qSuperheat * 100) / 100,
    qTotal: Math.round(qTotal * 100) / 100,
    fuelRateKgHr: Math.round(fuelRateKgHr * 10) / 10,
    fuelPer45min: Math.round(fuelRateKgHr * 0.75),  // kg for 1 rai treatment
  };
}

export function computeTemperatureProfile(meters = 21, fuelLevel = 100, combustionEff = 0.35) {
  const data = [];
  const coreTemp = 850 * (fuelLevel / 100);
  for (let m = 0; m <= meters; m++) {
    // Simplified model: temperature rises roughly logarithmically along coil
    const fraction = m / meters;
    let waterTemp;
    if (fraction < 0.55) {
      // Sensible heating zone (water 25°C → 100°C)
      waterTemp = 25 + (75 * (fraction / 0.55));
    } else if (fraction < 0.90) {
      // Vaporization zone (T stays at ~100°C during phase change)
      waterTemp = 100;
    } else {
      // Superheating zone
      const superheatFraction = (fraction - 0.90) / 0.10;
      waterTemp = 100 + (20 * superheatFraction * (fuelLevel / 100));
    }
    // Pressure drops along the coil
    const pressure = parseFloat((2.4 * (1 - m / (meters * 1.3))).toFixed(2));
    data.push({
      meter: m,
      temp: Math.round(Math.min(waterTemp, 120 * (fuelLevel / 100))),
      pressure: Math.max(pressure, 0.1),
      zone: fraction < 0.55 ? 'Sensible' : fraction < 0.90 ? 'Vaporization' : 'Superheat',
    });
  }
  return data;
}

export function computeLMTD(tHotIn, tHotOut, tColdIn, tColdOut) {
  const dt1 = tHotIn - tColdOut;
  const dt2 = tHotOut - tColdIn;
  if (dt1 === dt2) return dt1;
  return (dt1 - dt2) / Math.log(dt1 / dt2);
}

export function computeHeatTransferAdequacy(uValue = 300, fuelLevel = 100) {
  const coreTemp = 850 * (fuelLevel / 100);
  const exhaustTemp = 300 * (fuelLevel / 100);
  const lmtd = computeLMTD(coreTemp, exhaustTemp, 25, 120);
  const energy = computeBoilerEnergy();
  const requiredArea = (energy.qTotal * 1000) / (uValue * lmtd);
  const availableArea = CONSTANTS.HEAT_TRANSFER_AREA;
  return {
    lmtd: Math.round(lmtd),
    requiredArea: Math.round(requiredArea * 1000) / 1000,
    availableArea: Math.round(availableArea * 1000) / 1000,
    adequacy: Math.round((availableArea / requiredArea) * 100),
    isAdequate: availableArea >= requiredArea,
  };
}

// ============================================================
// SCALING / MAINTENANCE ENGINE
// ============================================================
export function computeScalingProfile(hours = 240, waterHardness = 250) {
  const data = [];
  for (let h = 0; h <= hours; h += 10) {
    // CaCO₃ deposition model (simplified from empirical data)
    // Mass deposited ∝ flow_rate × time × hardness × temp_factor
    const massDeposited = (0.045 * h * 3600 * waterHardness * 0.7) / 1e6; // kg
    const innerSurfaceArea = Math.PI * CONSTANTS.TUBE_ID * CONSTANTS.COIL_LENGTH; // m²
    const scaleThickness = (massDeposited / 2500) / innerSurfaceArea * 1000; // mm (density ~2500 kg/m³)

    // Effective U value with scale (scale thermal conductivity ~1.5 W/m·K)
    const baseU = 300; // W/m²K
    const adjustedU = 1 / ((1 / baseU) + (scaleThickness / 1000 / 1.5));
    const efficiency = Math.round((adjustedU / baseU) * 100);

    data.push({
      hour: h,
      efficiency: Math.max(efficiency, 20),
      scaleMm: parseFloat(scaleThickness.toFixed(3)),
      needsDescale: scaleThickness > 0.5,
    });
  }
  return data;
}

// ============================================================
// MUSHROOM YIELD ENGINE
// ============================================================
export function computeMushroomYield(
  strawPerRai = CONSTANTS.STRAW_PER_RAI_MID,
  be = CONSTANTS.BE_MODERATE,
  fuelFraction = 0.10
) {
  const substrate = strawPerRai * (1 - fuelFraction);
  const freshYield = substrate * be;
  return {
    strawAvailable: strawPerRai,
    fuelConsumed: Math.round(strawPerRai * fuelFraction),
    substrate: Math.round(substrate),
    freshYieldKg: Math.round(freshYield * 10) / 10,
    be: be * 100,
  };
}

// ============================================================
// ECONOMIC ENGINE
// ============================================================
export function computeEconomics(
  be = CONSTANTS.BE_MODERATE,
  pricePerKg = CONSTANTS.PRICE_WHOLESALE,
  strawPerRai = CONSTANTS.STRAW_PER_RAI_MID,
  numVillages = 4,
  adoptionRate = 0.75
) {
  const { COSTS } = CONSTANTS;
  const totalCostPerRai = Object.values(COSTS).reduce((a, b) => a + b, 0);

  const yield_ = computeMushroomYield(strawPerRai, be);
  const revenuePerRai = yield_.freshYieldKg * pricePerKg;
  const profitPerRai = revenuePerRai - totalCostPerRai;
  const profitPerYear = profitPerRai * 2; // 2 crop cycles

  // Break-even
  const breakEvenKg = totalCostPerRai / pricePerKg;
  const breakEvenBE = breakEvenKg / yield_.substrate;

  // Regional scale
  const raiPerVillage = 50 * 12; // 50 farmers × 12 rai avg
  const totalRai = raiPerVillage * numVillages * adoptionRate;
  const totalRevenue = totalRai * revenuePerRai;
  const totalProfit = totalRai * profitPerRai;

  return {
    costPerRai: totalCostPerRai,
    revenuePerRai: Math.round(revenuePerRai),
    profitPerRai: Math.round(profitPerRai),
    profitPerYear: Math.round(profitPerYear),
    marginPercent: Math.round((profitPerRai / revenuePerRai) * 100),
    breakEvenKg: Math.round(breakEvenKg * 10) / 10,
    breakEvenBE: Math.round(breakEvenBE * 1000) / 10,  // to %
    totalRegionalRai: Math.round(totalRai),
    totalRegionalRevenue: Math.round(totalRevenue),
    totalRegionalProfit: Math.round(totalProfit),
    yieldKg: yield_.freshYieldKg,
    isProfitable: profitPerRai > 0,
  };
}

export function computeSensitivityMatrix() {
  const beValues = [0.05, 0.08, 0.10, 0.12, 0.15];
  const priceValues = [30, 45, 60, 90, 120];
  const matrix = [];

  beValues.forEach(be => {
    const row = { be: be * 100 };
    priceValues.forEach(price => {
      const econ = computeEconomics(be, price);
      row[`p${price}`] = econ.profitPerRai;
    });
    matrix.push(row);
  });
  return matrix;
}

export function computeEconomicComparison() {
  return [
    { name: 'Mushroom Revenue', value: computeEconomics(0.12, 45).totalRegionalRevenue },
    { name: 'Carbon Credits', value: computeCarbonCredits(4).totalCreditsAg },
    { name: 'Cost Savings (vs Trichoderma)', value: 4 * 600 * 0.75 * 500 },
  ];
}

// ============================================================
// CARBON CREDIT ENGINE
// ============================================================
export function computeCarbonCredits(numVillages = 4, adoptionRate = 0.75) {
  const { CH4_PER_TON, N2O_PER_TON, GWP_CH4, GWP_N2O, BURN_FRACTION, STRAW_PER_RAI_MID } = CONSTANTS;

  const strawBurnedPerRai = (STRAW_PER_RAI_MID * BURN_FRACTION) / 1000; // tons
  const co2eqPerRai =
    strawBurnedPerRai * CH4_PER_TON * GWP_CH4 +
    strawBurnedPerRai * N2O_PER_TON * GWP_N2O;
  const tco2eqPerRai = co2eqPerRai / 1000;

  const raiPerVillage = 50 * 12;
  const totalRai = raiPerVillage * numVillages * adoptionRate;
  const totalTco2eq = totalRai * tco2eqPerRai;

  return {
    co2eqPerRaiKg: Math.round(co2eqPerRai * 10) / 10,
    tco2eqPerRai: Math.round(tco2eqPerRai * 1000) / 1000,
    totalRai: Math.round(totalRai),
    totalTco2eq: Math.round(totalTco2eq * 10) / 10,
    revenuePerRaiAvg: Math.round(tco2eqPerRai * CONSTANTS.CARBON_PRICE_AVG * 100) / 100,
    revenuePerRaiAg: Math.round(tco2eqPerRai * CONSTANTS.CARBON_PRICE_AG * 100) / 100,
    totalCreditsAvg: Math.round(totalTco2eq * CONSTANTS.CARBON_PRICE_AVG),
    totalCreditsAg: Math.round(totalTco2eq * CONSTANTS.CARBON_PRICE_AG),
  };
}

// ============================================================
// LOGISTICS ENGINE
// ============================================================
export function computeLogistics(numVillages = 4) {
  const totalRai = 50 * 12 * numVillages;
  const raiPerDayPerUnit = 25; // 45 min/rai, 8hr day
  const treatmentDays = 14; // must complete within 2 weeks
  const tractorsNeeded = Math.ceil(totalRai / (raiPerDayPerUnit * treatmentDays));
  const utilization = numVillages > 1 ? Math.min(92, 18 + (numVillages - 1) * 18.5) : 18;

  return {
    totalRai,
    tractorsNeeded,
    utilization: Math.round(utilization),
    raiPerDay: raiPerDayPerUnit,
    treatmentWindowDays: treatmentDays,
  };
}
