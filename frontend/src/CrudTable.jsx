import { useEffect, useState } from "react";
import { api } from "./api";

// A reusable table with add / edit / delete.
// `fields` describes the columns, e.g. { key: "points", label: "Pts", type: "number" }.
// `reloadKey` changes after a Wikipedia refresh, which tells this table to reload.
export default function CrudTable({ resource, fields, reloadKey }) {
  const emptyForm = Object.fromEntries(fields.map((f) => [f.key, ""]));

  const [rows, setRows] = useState([]); // data from the backend
  const [form, setForm] = useState(emptyForm); // values typed into the form
  const [editingId, setEditingId] = useState(null); // null = adding, a number = editing that row
  const [error, setError] = useState("");
  const [saveCount, setSaveCount] = useState(0); // bumped after each save to trigger a reload

  // Load rows when the component appears, and again whenever reloadKey or saveCount changes
  useEffect(() => {
    api
      .list(resource)
      .then((data) => {
        setRows(data);
        setError("");
      })
      .catch((err) => setError(err.message));
  }, [resource, reloadKey, saveCount]);

  // Form inputs are always text; convert them to what the API expects
  function formToPayload() {
    const payload = {};
    for (const f of fields) {
      const value = String(form[f.key]).trim();
      if (f.type === "number") payload[f.key] = Number(value);
      else payload[f.key] = value === "" && f.optional ? null : value;
    }
    return payload;
  }

  async function handleSubmit(event) {
    event.preventDefault(); // stop the browser reloading the page on submit
    try {
      if (editingId === null) await api.create(resource, formToPayload());
      else await api.update(resource, editingId, formToPayload());
      resetForm();
      setSaveCount((n) => n + 1);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(row) {
    if (!window.confirm("Delete this row?")) return;
    try {
      await api.remove(resource, row.id);
      setSaveCount((n) => n + 1);
    } catch (err) {
      setError(err.message);
    }
  }

  function startEditing(row) {
    setEditingId(row.id);
    // Copy the row's values into the form (null becomes "" so the input isn't empty-controlled)
    setForm(Object.fromEntries(fields.map((f) => [f.key, row[f.key] ?? ""])));
  }

  function resetForm() {
    setEditingId(null);
    setForm(emptyForm);
    setError("");
  }

  return (
    <section>
      <form className="row-form" onSubmit={handleSubmit}>
        <h3>{editingId === null ? "Add a row" : `Editing row #${editingId}`}</h3>
        <div className="fields">
          {fields.map((f) => (
            <label key={f.key}>
              {f.label}
              <input
                type={f.type === "number" ? "number" : "text"}
                value={form[f.key]}
                required={!f.optional}
                onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
              />
            </label>
          ))}
        </div>
        <div className="actions">
          <button type="submit">{editingId === null ? "Add" : "Save"}</button>
          {editingId !== null && (
            <button type="button" className="secondary" onClick={resetForm}>
              Cancel
            </button>
          )}
        </div>
      </form>

      {error && <p className="error">{error}</p>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {fields.map((f) => (
                <th key={f.key}>{f.label}</th>
              ))}
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td colSpan={fields.length + 1} className="empty">
                  No data yet. Click "Refresh from Wikipedia" or add a row.
                </td>
              </tr>
            )}
            {rows.map((row) => (
              <tr key={row.id} className={row.id === editingId ? "editing" : ""}>
                {fields.map((f) => (
                  <td key={f.key}>
                    {f.type === "url" && row[f.key] ? (
                      <a href={row[f.key]} target="_blank" rel="noreferrer">
                        link
                      </a>
                    ) : (
                      row[f.key]
                    )}
                  </td>
                ))}
                <td className="row-buttons">
                  <button className="secondary" onClick={() => startEditing(row)}>
                    Edit
                  </button>
                  <button className="danger" onClick={() => handleDelete(row)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
