const API = "http://127.0.0.1:8000";

export async function post(path, body) {
    const res = await fetch(API + path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });
    return res.json();
}

export async function get(path) {
    const res = await fetch(API + path);
    return res.json();
}