export const formatNumber = (n: number, digits = 0) =>
  n.toLocaleString(undefined, { maximumFractionDigits: digits })
