import { useState } from "react";
import { api } from "./api";
import CrudTable from "./CrudTable";

// Column setup for each table. `key` must match the field name in the backend schema.
const TEAM_FIELDS = [
  { key: "position", label: "Pos", type: "number" },
  { key: "name", label: "Team", type: "text" },
  { key: "played", label: "Played", type: "number" },
  { key: "won", label: "Won", type: "number" },
  { key: "drawn", label: "Drawn", type: "number" },
  { key: "lost", label: "Lost", type: "number" },
  { key: "goals_for", label: "GF", type: "number" },
  { key: "goals_against", label: "GA", type: "number" },
  { key: "goal_difference", label: "GD", type: "number" },
  { key: "points", label: "Points", type: "number" },
  { key: "wiki_url", label: "Wikipedia", type: "url", optional: true },
];

const SCORER_FIELDS = [
  { key: "rank", label: "Rank", type: "number" },
  { key: "player", label: "Player", type: "text" },
  { key: "club", label: "Club", type: "text" },
  { key: "goals", label: "Goals", type: "number" },
];

export default function App() {
  const [tab, setTab] = useState("teams");
  const [refreshing, setRefreshing] = useState(false);
  const [message, setMessage] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  async function handleRefresh() {
    if (!window.confirm("Replace all data with fresh data from Wikipedia? Manual edits will be lost.")) return;
    setRefreshing(true);
    setMessage("");
    try {
      const result = await api.scrape();
      setMessage(`Loaded ${result.teams} teams and ${result.scorers} scorers for ${result.season}.`);
      setReloadKey((k) => k + 1); // tells both tables to reload
    } catch (err) {
      setMessage(`Refresh failed: ${err.message}`);
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <main>
      <header>
        <h1>Premier League Stats</h1>
        <button onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? "Refreshing..." : "Refresh from Wikipedia"}
        </button>
      </header>
      {message && <p className="message">{message}</p>}

      <nav className="tabs">
        <button className={tab === "teams" ? "active" : ""} onClick={() => setTab("teams")}>
          League table
        </button>
        <button className={tab === "scorers" ? "active" : ""} onClick={() => setTab("scorers")}>
          Top scorers
        </button>
      </nav>

      {/* key={tab} gives each tab a fresh CrudTable, so the form resets when switching */}
      {tab === "teams" ? (
        <CrudTable key="teams" resource="teams" fields={TEAM_FIELDS} reloadKey={reloadKey} />
      ) : (
        <CrudTable key="scorers" resource="scorers" fields={SCORER_FIELDS} reloadKey={reloadKey} />
      )}
    </main>
  );
}
