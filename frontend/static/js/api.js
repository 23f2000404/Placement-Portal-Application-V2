// Small fetch wrapper
const Api = {
  async _request(method, url, body, isForm) {
    const opts = {
      method,
      credentials: "include", //Uses cookies from login sesh for auth
      headers: {},
    };
    if (body && !isForm) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    } else if (body && isForm) {
      opts.body = body; // FormData - browser sets content type incl boundary
    }
    const res = await fetch(url, opts);
    let data = null;
    try {
      data = await res.json();
    } catch (e) {
      data = null;
    }
    if (!res.ok) {
      const message = (data && data.error) || `Request failed (${res.status})`;
      throw new Error(message);
    }
    return data;
  },
  get(url) { return this._request("GET", url); },
  post(url, body) { return this._request("POST", url, body); },
  put(url, body) { return this._request("PUT", url, body); },
  postForm(url, formData) { return this._request("POST", url, formData, true); },
};
