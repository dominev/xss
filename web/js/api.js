const TutaApi = {
  token: localStorage.getItem("tuta_token") || "",
  user: localStorage.getItem("tuta_user") || "",

  headers() {
    const h = { "Content-Type": "application/json" };
    if (this.token) h.Authorization = `Bearer ${this.token}`;
    return h;
  },

  async get(url) {
    const res = await fetch(url, { headers: this.headers() });
    return res.json();
  },

  async post(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(body || {}),
    });
    return res.json();
  },

  save(session) {
    this.token = session.token;
    this.user = session.user;
    localStorage.setItem("tuta_token", session.token);
    localStorage.setItem("tuta_user", session.user);
  },

  clear() {
    this.token = "";
    this.user = "";
    localStorage.removeItem("tuta_token");
    localStorage.removeItem("tuta_user");
  },
};
