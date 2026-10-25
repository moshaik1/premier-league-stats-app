// All calls to the backend live here, so components don't deal with fetch() details.

async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    // FastAPI sends errors as {"detail": ...}. For validation errors (422) detail is a list.
    const body = await response.json().catch(() => ({}));
    const message =
      typeof body.detail === "string"
        ? body.detail
        : Array.isArray(body.detail)
          ? body.detail.map((d) => `${d.loc.at(-1)}: ${d.msg}`).join(", ")
          : `Request failed (${response.status})`;
    throw new Error(message);
  }

  // 204 No Content (after a delete) has no body to read
  return response.status === 204 ? null : response.json();
}

// `resource` is "teams" or "scorers"
export const api = {
  list: (resource) => request(`/${resource}`),
  create: (resource, data) =>
    request(`/${resource}`, { method: "POST", body: JSON.stringify(data) }),
  update: (resource, id, data) =>
    request(`/${resource}/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  remove: (resource, id) => request(`/${resource}/${id}`, { method: "DELETE" }),
  scrape: () => request("/scrape", { method: "POST" }),
};
