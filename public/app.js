let selectedEnergy = "Oil";

// -----------------------------
// PRICE (FROM API)
// -----------------------------
async function loadPrice() {
  const res = await fetch("/api/price");
  const data = await res.json();

  const benchmarks = [...new Set(data.map(d => d.benchmark))];

  const traces = benchmarks.map(b => ({
    x: data.filter(d => d.benchmark === b).map(d => d.period),
    y: data.filter(d => d.benchmark === b).map(d => d.value),
    name: b,
    mode: "lines",
    opacity: 0.45
  }));

  Plotly.newPlot("priceChart", traces, {
    hovermode: "x unified",
    height: 260
  });
}

// -----------------------------
// PROD vs CONS (FROM API)
// -----------------------------
async function loadProdCons() {
  const res = await fetch("/api/prod-cons");
  const data = await res.json();
  const rows = selectedEnergy === "Oil" ? data.oil : data.gas;

  document.getElementById("energyLabel").innerText =
    `Selected energy type: ${selectedEnergy}`;

  Plotly.newPlot("prodConsChart", [
    {
      x: rows.map(r => r.Year),
      y: rows.map(r => r.Production),
      name: "Production",
      mode: "lines",
      opacity: 0.45
    },
    {
      x: rows.map(r => r.Year),
      y: rows.map(r => r.Consumtion),
      name: "Consumption",
      mode: "lines",
      opacity: 0.45
    }
  ], {
    hovermode: "x unified",
    height: 260
  });
}

function setEnergy(type) {
  selectedEnergy = type;
  document.getElementById("oilBtn").classList.toggle("primary", type === "Oil");
  document.getElementById("gasBtn").classList.toggle("primary", type === "Gas");
  loadProdCons();
}

// -----------------------------
// DUMMY SUBSIDY
// -----------------------------
Plotly.newPlot("subsidyChart", [{
  x: [1.4, 3.4, 17.7, 26.9, 1.1],
  y: [2.1, 1.8, 0.9, 0.4, 3.2],
  text: ["Indonesia", "India", "China", "US", "Saudi"],
  mode: "markers",
  marker: { size: 12 }
}], { height: 260 });

// -----------------------------
// DUMMY MAP
// -----------------------------
Plotly.newPlot("mapChart", [{
  type: "choropleth",
  locations: ["USA", "SAU", "RUS", "CHN", "IND", "IDN"],
  z: [18.5, 12.1, 10.8, 4.2, 0.8, 0.7],
  text: ["US", "Saudi", "Russia", "China", "India", "Indonesia"]
}], { height: 420 });

// -----------------------------
// DUMMY NEWS
// -----------------------------
const news = [
  { title: "OPEC+ Considers Production Cut", src: "Reuters" },
  { title: "Middle East Tensions Push Oil Prices", src: "Bloomberg" },
  { title: "Energy Transition Impacts Demand", src: "IEA" }
];

document.getElementById("news").innerHTML = news.map(n =>
  `<p><b>${n.title}</b><br><small>${n.src}</small></p><hr>`
).join("");

// INIT
loadPrice();
loadProdCons();
