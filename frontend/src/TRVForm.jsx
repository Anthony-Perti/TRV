import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList, LineChart, ReferenceLine, Cell, Line } from "recharts";

const teamLogos = {
  PHI: "https://www.mlbstatic.com/team-logos/143.svg",
  ATL: "https://www.mlbstatic.com/team-logos/144.svg",
  NYM: "https://www.mlbstatic.com/team-logos/121.svg",
  MIA: "https://www.mlbstatic.com/team-logos/146.svg",
  WSN: "https://www.mlbstatic.com/team-logos/120.svg",
  CHC: "https://www.mlbstatic.com/team-logos/112.svg",
  MIL: "https://www.mlbstatic.com/team-logos/158.svg",
  STL: "https://www.mlbstatic.com/team-logos/138.svg",
  PIT: "https://www.mlbstatic.com/team-logos/134.svg",
  CIN: "https://www.mlbstatic.com/team-logos/113.svg",
  LAD: "https://www.mlbstatic.com/team-logos/119.svg",
  ARI: "https://www.mlbstatic.com/team-logos/109.svg",
  SDP: "https://www.mlbstatic.com/team-logos/135.svg",
  SFG: "https://www.mlbstatic.com/team-logos/137.svg",
  COL: "https://www.mlbstatic.com/team-logos/115.svg",
  NYY: "https://www.mlbstatic.com/team-logos/147.svg",
  BOS: "https://www.mlbstatic.com/team-logos/111.svg",
  TOR: "https://www.mlbstatic.com/team-logos/141.svg",
  BAL: "https://www.mlbstatic.com/team-logos/110.svg",
  TBR: "https://www.mlbstatic.com/team-logos/139.svg",
  CLE: "https://www.mlbstatic.com/team-logos/114.svg",
  DET: "https://www.mlbstatic.com/team-logos/116.svg",
  MIN: "https://www.mlbstatic.com/team-logos/142.svg",
  CHW: "https://www.mlbstatic.com/team-logos/145.svg",
  KCR: "https://www.mlbstatic.com/team-logos/118.svg",
  HOU: "https://www.mlbstatic.com/team-logos/117.svg",
  SEA: "https://www.mlbstatic.com/team-logos/136.svg",
  LAA: "https://www.mlbstatic.com/team-logos/108.svg",
  OAK: "https://www.mlbstatic.com/team-logos/133.svg",
  TEX: "https://www.mlbstatic.com/team-logos/140.svg",
};

const teamColors = {
  PHI: "#E81828",
  ATL: "#CE1141",
  NYM: "#002D72",
  MIA: "#00A3E0",
  WSN: "#AB0003",
  CHC: "#0E3386",
  MIL: "#12284B",
  STL: "#C41E3A",
  PIT: "#FDB827",
  CIN: "#C6011F",
  LAD: "#005A9C",
  ARI: "#A71930",
  SDP: "#2F241D",
  SFG: "#FD5A1E",
  COL: "#33006F",
  NYY: "#003087",
  BOS: "#BD3039",
  TOR: "#134A8E",
  BAL: "#DF4601",
  TBR: "#092C5C",
  CLE: "#E31937",
  DET: "#0C2340",
  MIN: "#002B5C",
  CHW: "#27251F",
  KCR: "#004687",
  HOU: "#002D62",
  SEA: "#005C5C",
  LAA: "#BA0021",
  OAK: "#003831",
  TEX: "#003278",
};

const TRVForm = () => {
  const [teamName, setTeamName] = useState("PHI");
  const [players, setPlayers] = useState([]);
  const [teamPlayers, setTeamPlayers] = useState([]);
  const [weightScheme, setWeightScheme] = useState("Balanced");
  const [customWeightFields, setCustomWeightFields] = useState({
    offense: 1.0,
    defense: 1.0,
    contact: 1.0,
    power: 1.0,
    plate_discipline: 1.0,
    baserunning: 1.0,
  });
  const [averageOf, setAverageOf] = useState("");
  const [result, setResult] = useState(null);
  const [leagueTRV, setLeagueTRV] = useState(null);
  const [trvCurve, setTrvCurve] = useState(null);
  const [showHistogram, setShowHistogram] = useState(true);
  const [activeTab, setActiveTab] = useState("overview"); // "overview" or "team_trv"
  const [sortAscending, setSortAscending] = useState(false);

  const teamColor = teamColors[teamName] || "#3b82f6";
  const teamLogo = teamLogos[teamName];

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/players_for_team/?team_name=${teamName}`)
      .then((res) => res.json())
      .then((data) => setTeamPlayers(data.players || []));
    setPlayers([]);
  }, [teamName]);

  useEffect(() => {
    setResult(null);
    setLeagueTRV(null);
    setTrvCurve(null);
  }, [weightScheme, teamName, players, JSON.stringify(customWeightFields), averageOf]);
  
  function binTRVs(playerTRVs, binSize = 0.5) {
    const bins = {};
    for (const { trv } of playerTRVs) {
      const bin = (Math.floor(trv / binSize) * binSize).toFixed(1);
      bins[bin] = (bins[bin] || 0) + 1;
    }
    return Object.entries(bins)
      .sort((a, b) => parseFloat(a[0]) - parseFloat(b[0]))
      .map(([range, count]) => ({ range, count }));
  }
  
  function findBinIndex(trv, binSize = 0.5) {
    return (Math.floor(trv / binSize) * binSize).toFixed(1);
  }
  const handleSubmit = async () => {
    const payload = {
      team_name: teamName,
      player_names: players,
      weight_scheme: weightScheme,
    };

    if (weightScheme.toLowerCase() === "custom") {
      payload.custom_weights = { ...customWeightFields };
    } else if (weightScheme.toLowerCase() === "averageof") {
      payload.average_of = averageOf.split(",").map((s) => s.trim()).filter(Boolean);
    }

    const [res1, res2, res3] = await Promise.all([
      fetch("http://127.0.0.1:8000/compute_trv/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
      fetch("http://127.0.0.1:8000/league_trv/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
      fetch("http://127.0.0.1:8000/trv_distribution/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
    ]);

    if (!res1.ok || !res2.ok || !res3.ok) {
      console.error("One of the API requests failed");
      return;
    }
    
    const [data1, data2, data3] = await Promise.all([res1.json(), res2.json(), res3.json()]);
    setResult(data1);
    setLeagueTRV(data2);
    setTrvCurve(data3.x.map((xVal, idx) => ({ x: xVal, y: data3.y[idx] })));
  };

  const teamLabels = {
    PHI: "Philadelphia Phillies",
    ATL: "Atlanta Braves",
    NYM: "New York Mets",
    MIA: "Miami Marlins",
    WSN: "Washington Nationals",
    CHC: "Chicago Cubs",
    MIL: "Milwaukee Brewers",
    STL: "St. Louis Cardinals",
    PIT: "Pittsburgh Pirates",
    CIN: "Cincinnati Reds",
    LAD: "Los Angeles Dodgers",
    ARI: "Arizona Diamondbacks",
    SDP: "San Diego Padres",
    SFG: "San Francisco Giants",
    COL: "Colorado Rockies",
    NYY: "New York Yankees",
    BOS: "Boston Red Sox",
    TOR: "Toronto Blue Jays",
    BAL: "Baltimore Orioles",
    TBR: "Tampa Bay Rays",
    CLE: "Cleveland Guardians",
    DET: "Detroit Tigers",
    MIN: "Minnesota Twins",
    CHW: "Chicago White Sox",
    KCR: "Kansas City Royals",
    HOU: "Houston Astros",
    SEA: "Seattle Mariners",
    LAA: "Los Angeles Angels",
    OAK: "Oakland Athletics",
    TEX: "Texas Rangers",
  };

  const divisions = {
    "NL East": ["PHI", "ATL", "NYM", "MIA", "WSN"],
    "NL Central": ["CHC", "MIL", "STL", "PIT", "CIN"],
    "NL West": ["LAD", "ARI", "SDP", "SFG", "COL"],
    "AL East": ["NYY", "BOS", "TOR", "BAL", "TBR"],
    "AL Central": ["CLE", "DET", "MIN", "CHW", "KCR"],
    "AL West": ["HOU", "SEA", "LAA", "OAK", "TEX"],
  };

  function padLeagueTeamTRVs(rawTRVs) {
    return Object.keys(teamLabels).map((teamCode) => {
      const found = rawTRVs.find((t) => t.team === teamCode);
      return {
        team: teamCode,
        trv: found ? found.trv : null
      };
    });
  }

  const sortedPaddedTeamTRVs = leagueTRV ? [...padLeagueTeamTRVs(leagueTRV.team_trvs)].sort((a, b) => {
    if (a.trv === null) return 1;
    if (b.trv === null) return -1;
    return sortAscending ? a.trv - b.trv : b.trv - a.trv;
  }) : [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 space-y-6 max-w-3xl mx-auto"
    >
      {teamLogo && (
        <div className="flex justify-center mb-4">
          <div className="h-16 w-16 flex items-center justify-center">
            <img
              src={teamLogo}
              alt={`${teamName} logo`}
              style={{
                height: '32px',
                width: '32px',
                objectFit: 'contain',
              }}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <label className="font-medium">{teamLabels[teamName]}</label>
          </div>
          <select
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            className="w-full p-2 border rounded"
          >
            {Object.entries(divisions).map(([division, teams]) => (
              <optgroup key={division} label={division}>
                {teams.map((code) => (
                  <option key={code} value={code}>{teamLabels[code]}</option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-medium mb-1">Select Players</label>
          <div className="border p-2 rounded max-h-40 overflow-y-auto">
            {teamPlayers.map((name) => (
              <div key={name} className="flex items-center">
                <input
                  type="checkbox"
                  id={name}
                  value={name}
                  checked={players.includes(name)}
                  onChange={(e) => {
                    const selected = [...players];
                    if (e.target.checked) selected.push(name);
                    else selected.splice(selected.indexOf(name), 1);
                    setPlayers(selected);
                  }}
                  className="mr-2"
                />
                <label htmlFor={name}>{name}</label>
              </div>
            ))}
          </div>
        </div>
      </div>
            
      <div>
        <label className="block font-medium mb-1">Weight Scheme</label>
        <select
          value={weightScheme}
          onChange={(e) => setWeightScheme(e.target.value)}
          className="w-full p-2 border rounded"
        >
          <option value="Balanced">Balanced</option>
          <option value="Offense">OffenseHeavy</option>
          <option value="Prevention">DefenseHeavy</option>
          <option value="Custom">Custom</option>
          <option value="ML">ML</option>
          <option value="AverageOf">AverageOf</option>
        </select>
      </div>

      {weightScheme.toLowerCase() === "averageof" && (
        <div>
          <label className="block font-medium mb-1">Average Of (comma-separated)</label>
          <input
            className="w-full p-2 border rounded"
            value={averageOf}
            onChange={(e) => setAverageOf(e.target.value)}
          />
        </div>
      )}

      {weightScheme.toLowerCase() === "custom" && (
        <div>
          <h3 className="font-medium">Custom Weights</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {Object.entries(customWeightFields).map(([key, value]) => (
              <div key={key}>
                <label className="text-sm capitalize">{key.replace("_", " ")}</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  value={value}
                  onChange={(e) =>
                    setCustomWeightFields({
                      ...customWeightFields,
                      [key]: parseFloat(e.target.value) || 0,
                    })
                  }
                  className="w-full p-1 border rounded"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={players.length === 0}
        className={`w-full py-2 rounded text-white font-semibold transition-colors duration-200 ${
          players.length === 0 ? "bg-gray-400 cursor-not-allowed" : ""
        }`}
        style={{ backgroundColor: players.length === 0 ? "" : teamColor }}
      >
        Compute TRV
      </button>
      
      <div className="flex justify-center mb-6 space-x-4">
        <button
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2 rounded ${
            activeTab === "overview" ? "bg-blue-600 text-white" : "bg-gray-200"
          }`}
        >
          View Player TRV
        </button>
        <button
          onClick={() => setActiveTab("team_trv")}
          className={`px-4 py-2 rounded ${
            activeTab === "team_trv" ? "bg-blue-600 text-white" : "bg-gray-200"
          }`}
        >
          View Team TRVs
        </button>
      </div> 

      {activeTab === "team_trv" && leagueTRV && (
        <motion.div className="p-4 border rounded bg-white shadow space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold">League Team TRVs</h2>
            <button
              onClick={() => setSortAscending(!sortAscending)}
              className="px-3 py-1 text-sm border rounded shadow"
            >
              Sort: {sortAscending ? "Ascending" : "Descending"}
            </button>
          </div>

          <ResponsiveContainer width="100%" height={900}>
            <BarChart
              data={sortedPaddedTeamTRVs}
              layout="vertical"
              margin={{ top: 20, left: 100, right: 30 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis
                type="category"
                dataKey="team"
                width={140}
                tickFormatter={(code) => teamLabels[code] || code}
              />
              <Tooltip />
              <Bar dataKey="trv" isAnimationActive={false}>
                {sortedPaddedTeamTRVs.map((entry) => (
                  <Cell
                    key={entry.team}
                    fill={entry.team === result?.team ? teamColor : "#ccc"}
                  />
                ))}
                <LabelList dataKey="trv" position="right" formatter={(v) => v?.toFixed(2)} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      )}

      {result && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-4 border rounded bg-gray-50 shadow"
          style={{ borderTop: `4px solid ${teamColor}` }}
        >
          <h2 className="text-lg font-semibold mb-2">TRV Results</h2>
          <p className="mb-4">
            Team: <strong>{result.team}</strong> | Total TRV: <strong>{result.total_trv.toFixed(2)}</strong> | Scheme: <strong>{result.weight_scheme}</strong>
          </p>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={result.players} layout="vertical" margin={{ left: 30 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={["auto", "auto"]} />
              <YAxis type="category" dataKey="name" width={100} />
              <Tooltip />
              <Bar dataKey="trv" fill={teamColor} />
            </BarChart>
          </ResponsiveContainer>

          <div className="mt-4">
            <h3 className="font-semibold">Used Weights:</h3>
            <ul className="list-disc list-inside">
              {Object.entries(result.used_weights).map(([k, v]) => (
                <li key={k}>{k.replace("_", " ")}: {v.toFixed(3)}</li>
              ))}
            </ul>
          </div>
        </motion.div>
      )}
      {leagueTRV && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 border rounded bg-white shadow space-y-8">
          <h2 className="text-lg font-semibold mb-2">League TRV Comparison</h2> 
          <div className="flex justify-end mb-2">
            <button
              onClick={() => setShowHistogram((prev) => !prev)}
              className="px-3 py-1 text-sm border rounded shadow"
            >
              {showHistogram ? "Show Bell Curve" : "Show Histogram"}
            </button>
          </div>

          {showHistogram ? (
            // Histogram
            <div>
              <h3 className="font-medium mb-1">Player TRV Distribution (Histogram)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={binTRVs(leagueTRV.player_trvs)}
                  margin={{ top: 10, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" label={{ value: "TRV", position: "insideBottom", offset: -5 }} />
                  <YAxis label={{ value: "Players", angle: -90, position: "insideLeft" }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                  <ReferenceLine x={findBinIndex(0)} stroke="black" strokeDasharray="3 3" label="League Avg" />
                  {result.players.map((p) => (
                    <ReferenceLine
                      key={p.name}
                      x={findBinIndex(p.trv)}
                      stroke={teamColor}
                      strokeDasharray="5 5"
                      label={{
                        value: `${p.name}`,
                        angle: 0,
                        position: "top-middle",
                        fill: teamColor,
                        fontSize: 12,
                        dy: -10
                      }}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            // Bell Curve
            trvCurve && (
              <div>
                {console.log("TRV values:", result?.players?.map(p => ({ name: p.name, trv: p.trv })))}
                <h3 className="font-medium mb-1">TRV Bell Curve</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={trvCurve}
                    margin={{ top: 10, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="x"
                      type="number"
                      domain={["dataMin", "dataMax"]}
                      label={{ value: "TRV", position: "insideBottom", offset: -5 }}
                    />
                    <YAxis
                      label={{ value: "Density", angle: -90, position: "insideLeft" }}
                    />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="y"
                      stroke="#82ca9d"
                      dot={false}
                      strokeWidth={2}
                      isAnimationActive={false}
                    />
                    <ReferenceLine
                      x={0}
                      stroke="black"
                      strokeDasharray="4 4"
                      label={{
                        value: "League Avg",
                        position: "middle",
                        fill: "black",
                        fontSize: 12,
                        dy: -10,
                      }}
                    />
                    {/* Selected Player Markers */}
                    {result.players.map((p) => {
                      const closestPoint = trvCurve.reduce((prev, curr) =>
                        Math.abs(curr.x - p.trv) < Math.abs(prev.x - p.trv) ? curr : prev
                      );

                      return (
                        <ReferenceLine
                          key={p.name}
                          x={closestPoint.x}
                          stroke={teamColor}
                          strokeDasharray="5 5"
                          label={{
                            value: `${p.name}`,
                            angle: 0,
                            position: "middle",
                            fill: teamColor,
                            fontSize: 12,
                            dy: -10,
                          }}
                        />
                      );
                    })}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )
          )}
        </motion.div>
      )}
    </motion.div>
  );
};

export default TRVForm;